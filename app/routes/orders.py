from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import OrderCreate
from app.routes.cart import calculate_cart_bill
import uuid
import datetime

router = APIRouter(prefix="/api/orders", tags=["orders"])

USER_ID = 1

RIDERS = [
    {"name": "Vikram Sharma", "phone": "+91 98765 43210", "vehicle": "Ather 450X (Electric)", "rating": 4.9},
    {"name": "Rohan Verma", "phone": "+91 98112 34567", "vehicle": "TVS iQube (Electric)", "rating": 4.8},
    {"name": "Arjun Patel", "phone": "+91 99201 87654", "vehicle": "Ola S1 Pro", "rating": 4.95}
]

@router.post("/checkout")
def checkout_order(body: OrderCreate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Fetch current cart
    cursor.execute("""
        SELECT c.quantity, p.* 
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
    """, (USER_ID,))
    cart_rows = cursor.fetchall()
    
    if not cart_rows:
        conn.close()
        raise HTTPException(status_code=400, detail="Your cart is empty. Add items to checkout!")
        
    items = [dict(r) for r in cart_rows]
    bill = calculate_cart_bill(items, coupon_code=body.coupon_code, tip=body.tip)
    total_to_pay = bill["final_amount"]
    
    # 2. Get delivery address
    if body.address_id:
        cursor.execute("SELECT * FROM addresses WHERE id = ? AND user_id = ?", (body.address_id, USER_ID))
    else:
        cursor.execute("SELECT * FROM addresses WHERE user_id = ? ORDER BY is_default DESC, id DESC LIMIT 1", (USER_ID,))
    addr_row = cursor.fetchone()
    
    if addr_row:
        address_snapshot = f"{addr_row['tag']}: {addr_row['address_line']}, {addr_row['landmark'] or ''}, {addr_row['city']} - {addr_row['pincode']}"
    else:
        address_snapshot = "Home: Flat 402, Sunshine Towers, Park Avenue, Bhubaneswar - 751001"
        
    # 3. Handle payment method
    payment_method = body.payment_method.lower()
    
    if payment_method == "wallet":
        cursor.execute("SELECT balance FROM wallets WHERE user_id = ?", (USER_ID,))
        w_row = cursor.fetchone()
        wallet_balance = w_row["balance"] if w_row else 0.0
        
        if wallet_balance < total_to_pay:
            conn.close()
            raise HTTPException(
                status_code=400, 
                detail=f"Insufficient wallet balance (₹{wallet_balance:.2f}). Required ₹{total_to_pay:.2f}. Please top up your wallet or choose UPI/Card/COD."
            )
            
        # Deduct wallet
        new_balance = wallet_balance - total_to_pay
        cursor.execute("UPDATE wallets SET balance = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?", (new_balance, USER_ID))
        
    # 4. Generate order
    order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    rider = RIDERS[hash(order_number) % len(RIDERS)]
    
    cursor.execute("""
        INSERT INTO orders (
            order_number, user_id, item_total, delivery_fee, handling_fee,
            tip, discount, coupon_code, total_amount, payment_method,
            payment_status, order_status, delivery_address_snapshot,
            rider_name, rider_phone
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'completed', 'placed', ?, ?, ?)
    """, (
        order_number, USER_ID, bill["item_total"], bill["delivery_fee"],
        bill["handling_fee"], bill["tip"], bill["coupon_discount"],
        bill["coupon_code"], total_to_pay, payment_method,
        address_snapshot, rider["name"], rider["phone"]
    ))
    order_id = cursor.lastrowid
    
    # 5. Insert order items
    for item in items:
        cursor.execute("""
            INSERT INTO order_items (
                order_id, product_id, product_name, price, quantity, unit, image_url
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id, item["id"], item["name"], item["price"],
            item["quantity"], item["unit"], item["image_url"]
        ))
        
    # 6. Record wallet transaction if paid by wallet
    if payment_method == "wallet":
        cursor.execute("""
            INSERT INTO wallet_transactions (user_id, amount, type, title, reference_id)
            VALUES (?, ?, 'debit', ?, ?)
        """, (USER_ID, total_to_pay, f"Payment for Order #{order_number}", order_number))
        
    # 7. Clear the cart
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (USER_ID,))
    
    conn.commit()
    conn.close()
    
    return {
        "status": "success",
        "order_id": order_id,
        "order_number": order_number,
        "total_amount": total_to_pay,
        "payment_method": payment_method,
        "delivery_eta": "10 MINS",
        "rider": rider,
        "message": "Order placed successfully! Delivery partner arriving in 10 minutes."
    }

@router.get("")
def list_orders():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM orders 
        WHERE user_id = ? 
        ORDER BY id DESC
    """, (USER_ID,))
    orders = [dict(r) for r in cursor.fetchall()]
    
    for o in orders:
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (o["id"],))
        o["items"] = [dict(r) for r in cursor.fetchall()]
        
    conn.close()
    return {"orders": orders}

@router.get("/{order_id}")
def get_order_by_id(order_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, USER_ID))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = dict(order_row)
    cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
    order["items"] = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {"order": order}

@router.get("/{order_id}/tracking")
def get_order_tracking(order_id: int):
    """Simulates real-time 10-minute delivery stages and live GPS rider progress."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM orders WHERE id = ? AND user_id = ?", (order_id, USER_ID))
    order_row = cursor.fetchone()
    if not order_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found")
        
    order = dict(order_row)
    created_str = order["created_at"]
    
    # Calculate elapsed seconds since placement
    try:
        created_time = datetime.datetime.fromisoformat(created_str)
    except Exception:
        created_time = datetime.datetime.now()
        
    now = datetime.datetime.now()
    elapsed_seconds = (now - created_time).total_seconds()
    if elapsed_seconds < 0:
        elapsed_seconds = 5
        
    # Quick commerce simulation timing:
    # 0 - 25s: Placed & Confirmed at Dark Store
    # 25 - 55s: Packed with ice pack & fresh seal
    # 55 - 100s: Rider Out for Delivery (on scooter)
    # 100s+: Delivered
    
    if elapsed_seconds < 25:
        stage = "order_placed"
        stage_text = "Order Placed & Confirmed"
        sub_text = "Dark Store #104 has accepted your order"
        progress_pct = 20
        eta_minutes = 9
    elif elapsed_seconds < 55:
        stage = "packed"
        stage_text = "Packed & Temperature Checked"
        sub_text = "Packer has double-checked all items and bagged them"
        progress_pct = 45
        eta_minutes = 7
    elif elapsed_seconds < 100:
        stage = "out_for_delivery"
        stage_text = "Out for Delivery on Electric Scooter"
        sub_text = f"{order['rider_name']} is 0.8 km away driving safely"
        progress_pct = 75
        eta_minutes = 3
    else:
        stage = "delivered"
        stage_text = "Delivered at Doorstep!"
        sub_text = "Package delivered with OTP confirmation. Enjoy fresh goods!"
        progress_pct = 100
        eta_minutes = 0
        
    stages = [
        {"key": "order_placed", "title": "Order Placed", "desc": "Received at local dark store", "done": elapsed_seconds >= 5, "current": stage == "order_placed"},
        {"key": "packed", "title": "Items Packed", "desc": "Quality & chilled packing complete", "done": elapsed_seconds >= 25, "current": stage == "packed"},
        {"key": "out_for_delivery", "title": "Out for Delivery", "desc": f"Rider {order['rider_name']} on route", "done": elapsed_seconds >= 55, "current": stage == "out_for_delivery"},
        {"key": "delivered", "title": "Delivered", "desc": "Arrived at your location", "done": elapsed_seconds >= 100, "current": stage == "delivered"}
    ]
    
    conn.close()
    
    return {
        "order_number": order["order_number"],
        "stage": stage,
        "stage_text": stage_text,
        "sub_text": sub_text,
        "progress_pct": progress_pct,
        "eta_minutes": eta_minutes,
        "elapsed_seconds": int(elapsed_seconds),
        "rider": {
            "name": order["rider_name"],
            "phone": order["rider_phone"],
            "vehicle": "Ather 450X · KA 01 EQ 4421",
            "rating": 4.9,
            "deliveries_today": 24
        },
        "delivery_address": order["delivery_address_snapshot"],
        "stages": stages
    }
