from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import UserLogin, UserProfileUpdate, AddressCreate

router = APIRouter(prefix="/api/user", tags=["user"])

USER_ID = 1

@router.get("/profile")
def get_profile():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, phone, name, email, created_at FROM users WHERE id = ?", (USER_ID,))
    user = cursor.fetchone()
    if not user:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
        
    cursor.execute("SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC, id DESC", (USER_ID,))
    addresses = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        "user": dict(user),
        "addresses": addresses
    }

@router.post("/login")
def login(body: UserLogin):
    phone = body.phone.strip()
    if len(phone) < 10:
        raise HTTPException(status_code=400, detail="Please enter a valid 10-digit mobile number")
        
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if user with phone exists, else update or keep user 1
    cursor.execute("SELECT id, phone, name, email FROM users WHERE id = ?", (USER_ID,))
    user = cursor.fetchone()
    if user:
        cursor.execute("UPDATE users SET phone = ? WHERE id = ?", (phone, USER_ID))
    else:
        cursor.execute("INSERT INTO users (id, phone, name, email) VALUES (?, ?, 'Verified Shopper', 'user@quickmart.in')", (USER_ID, phone))
        
    conn.commit()
    
    cursor.execute("SELECT id, phone, name, email FROM users WHERE id = ?", (USER_ID,))
    updated_user = dict(cursor.fetchone())
    conn.close()
    
    return {
        "status": "success",
        "message": "Login successful! Welcome back to Quick Commerce.",
        "user": updated_user
    }

@router.put("/profile")
def update_profile(body: UserProfileUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    updates = []
    params = []
    if body.name is not None:
        updates.append("name = ?")
        params.append(body.name)
    if body.email is not None:
        updates.append("email = ?")
        params.append(body.email)
        
    if updates:
        params.append(USER_ID)
        cursor.execute(f"UPDATE users SET {', '.join(updates)} WHERE id = ?", params)
        conn.commit()
        
    cursor.execute("SELECT id, phone, name, email FROM users WHERE id = ?", (USER_ID,))
    user = dict(cursor.fetchone())
    conn.close()
    
    return {"status": "success", "user": user}

@router.get("/addresses")
def get_addresses():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC, id DESC", (USER_ID,))
    addresses = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"addresses": addresses}

@router.post("/addresses")
def add_address(body: AddressCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if body.is_default:
        cursor.execute("UPDATE addresses SET is_default = 0 WHERE user_id = ?", (USER_ID,))
        
    cursor.execute("""
        INSERT INTO addresses (user_id, tag, address_line, landmark, city, pincode, is_default)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (USER_ID, body.tag, body.address_line, body.landmark, body.city, body.pincode, 1 if body.is_default else 0))
    
    addr_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return {"status": "success", "address_id": addr_id, "message": "Address added successfully"}

@router.put("/addresses/{address_id}/default")
def set_default_address(address_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE addresses SET is_default = 0 WHERE user_id = ?", (USER_ID,))
    cursor.execute("UPDATE addresses SET is_default = 1 WHERE id = ? AND user_id = ?", (address_id, USER_ID))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Default address updated"}

@router.delete("/addresses/{address_id}")
def delete_address(address_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM addresses WHERE id = ? AND user_id = ?", (address_id, USER_ID))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Address deleted"}
