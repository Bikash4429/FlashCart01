from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import WalletTopUp
import uuid

router = APIRouter(prefix="/api/wallet", tags=["wallet"])

USER_ID = 1

@router.get("")
def get_wallet():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Balance
    cursor.execute("SELECT balance FROM wallets WHERE user_id = ?", (USER_ID,))
    row = cursor.fetchone()
    balance = row["balance"] if row else 0.0
    
    # Transactions
    cursor.execute("""
        SELECT * FROM wallet_transactions 
        WHERE user_id = ? 
        ORDER BY created_at DESC 
        LIMIT 30
    """, (USER_ID,))
    tx_rows = cursor.fetchall()
    transactions = [dict(r) for r in tx_rows]
    
    conn.close()
    return {
        "user_id": USER_ID,
        "balance": round(balance, 2),
        "transactions": transactions
    }

@router.post("/topup")
def topup_wallet(body: WalletTopUp):
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Top up amount must be greater than 0")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Upsert wallet
    cursor.execute("SELECT balance FROM wallets WHERE user_id = ?", (USER_ID,))
    row = cursor.fetchone()
    if row:
        new_balance = row["balance"] + body.amount
        cursor.execute("UPDATE wallets SET balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", (new_balance, USER_ID))
    else:
        new_balance = body.amount
        cursor.execute("INSERT INTO wallets (user_id, balance) VALUES (?, ?)", (USER_ID, new_balance))
        
    # Add transaction log
    ref = f"TOPUP-{uuid.uuid4().hex[:8].upper()}"
    channel = body.payment_channel or "Instant Pay"
    cursor.execute("""
        INSERT INTO wallet_transactions (user_id, amount, type, title, reference_id)
        VALUES (?, ?, 'credit', ?, ?)
    """, (USER_ID, body.amount, f"Money Added via {channel}", ref))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "new_balance": round(new_balance, 2),
        "amount_added": body.amount,
        "reference_id": ref,
        "message": f"₹{body.amount:.2f} successfully credited to your Quick Wallet!"
    }
