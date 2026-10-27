from fastapi import APIRouter, HTTPException, Query
from app.database import get_db_connection
from app.models import CartItemAdd, CartItemUpdate
from typing import Optional

router = APIRouter(prefix="/api/cart", tags=["cart"])

USER_ID = 1  # Default active user

def calculate_cart_bill(items, coupon_code=None, tip=0.0):
    item_total = sum(item["price"] * item["quantity"] for item in items)
    mrp_total = sum(item["mrp"] * item["quantity"] for item in items)
    product_discount = max(0.0, mrp_total - item_total)
    
    # Quick commerce delivery rule: Free delivery above ₹199, else ₹15
    if item_total == 0:
        delivery_fee = 0.0
    elif item_total >= 199:
        delivery_fee = 0.0
    else:
        delivery_fee = 15.0
        
    handling_fee = 5.0 if item_total > 0 else 0.0
    
    # Coupon validation
    coupon_discount = 0.0
    applied_coupon = None
    coupon_message = None
    
    if coupon_code:
        code = coupon_code.strip().upper()
        if code == "QUICK100":
            if item_total >= 399:
                coupon_discount = 100.0
                applied_coupon = code
                coupon_message = "₹100 SAVED WITH QUICK100"
            else:
                coupon_message = "Add items worth ₹" + str(round(399 - item_total)) + " more to apply QUICK100"
        elif code == "WELCOME50":
            if item_total >= 199:
                coupon_discount = 50.0
                applied_coupon = code
                coupon_message = "₹50 SAVED WITH WELCOME50"
            else:
                coupon_message = "Add items worth ₹" + str(round(199 - item_total)) + " more to apply WELCOME50"
        elif code == "FREEDEL":
            if delivery_fee > 0:
                coupon_discount = delivery_fee
                applied_coupon = code
                coupon_message = "FREE DELIVERY COUPON APPLIED"
            else:
                coupon_message = "Delivery is already free on your cart!"
        else:
            coupon_message = "Invalid coupon code"
            
    final_amount = max(0.0, item_total + delivery_fee + handling_fee + tip - coupon_discount)
    total_savings = product_discount + coupon_discount
    
    return {
        "item_total": round(item_total, 2),
        "mrp_total": round(mrp_total, 2),
        "product_discount": round(product_discount, 2),
        "delivery_fee": round(delivery_fee, 2),
        "handling_fee": round(handling_fee, 2),
        "tip": round(tip, 2),
        "coupon_code": applied_coupon,
        "coupon_discount": round(coupon_discount, 2),
        "coupon_message": coupon_message,
        "final_amount": round(final_amount, 2),
        "total_savings": round(total_savings, 2),
        "item_count": sum(item["quantity"] for item in items),
        "free_delivery_threshold": 199.0,
        "free_delivery_needed": max(0.0, round(199.0 - item_total, 2)) if item_total < 199 and item_total > 0 else 0.0
    }

@router.get("")
def get_cart(coupon: Optional[str] = None, tip: float = 0.0):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT c.id as cart_id, c.quantity, p.* 
        FROM cart c
        JOIN products p ON c.product_id = p.id
        WHERE c.user_id = ?
        ORDER BY c.updated_at DESC
    """, (USER_ID,))
    rows = cursor.fetchall()
    
    items = []
    for r in rows:
        item = dict(r)
        item["line_total"] = round(item["price"] * item["quantity"], 2)
        items.append(item)
        
    bill = calculate_cart_bill(items, coupon_code=coupon, tip=tip)
    conn.close()
    
    return {
        "items": items,
        "bill": bill
    }

@router.post("/add")
def add_to_cart(item: CartItemAdd):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check product existence & stock
    cursor.execute("SELECT id, in_stock, name FROM products WHERE id = ?", (item.product_id,))
    prod = cursor.fetchone()
    if not prod:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    if not prod["in_stock"]:
        conn.close()
        raise HTTPException(status_code=400, detail=f"'{prod['name']}' is currently out of stock")
        
    # Upsert into cart
    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (USER_ID, item.product_id))
    row = cursor.fetchone()
    if row:
        new_qty = row["quantity"] + item.quantity
        cursor.execute("""
            UPDATE cart SET quantity = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE user_id = ? AND product_id = ?
        """, (new_qty, USER_ID, item.product_id))
    else:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity) 
            VALUES (?, ?, ?)
        """, (USER_ID, item.product_id, item.quantity))
        
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Product added to cart"}

@router.post("/update")
def update_cart_item(item: CartItemUpdate):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if item.quantity <= 0:
        cursor.execute("DELETE FROM cart WHERE user_id = ? AND product_id = ?", (USER_ID, item.product_id))
    else:
        cursor.execute("""
            INSERT INTO cart (user_id, product_id, quantity, updated_at)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(user_id, product_id) DO UPDATE SET
            quantity = excluded.quantity,
            updated_at = CURRENT_TIMESTAMP
        """, (USER_ID, item.product_id, item.quantity))
        
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Cart updated"}

@router.post("/clear")
def clear_cart():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cart WHERE user_id = ?", (USER_ID,))
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Cart emptied"}
