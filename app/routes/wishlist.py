from fastapi import APIRouter, HTTPException
from app.database import get_db_connection
from app.models import WishlistToggle

router = APIRouter(prefix="/api/wishlist", tags=["wishlist"])

USER_ID = 1

@router.get("")
def get_wishlist():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT w.id as wishlist_id, w.created_at as saved_at, p.* 
        FROM wishlist w
        JOIN products p ON w.product_id = p.id
        WHERE w.user_id = ?
        ORDER BY w.created_at DESC
    """, (USER_ID,))
    items = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return {"items": items, "count": len(items)}

@router.post("/toggle")
def toggle_wishlist(body: WishlistToggle):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?", (USER_ID, body.product_id))
    existing = cursor.fetchone()
    
    if existing:
        cursor.execute("DELETE FROM wishlist WHERE user_id = ? AND product_id = ?", (USER_ID, body.product_id))
        conn.commit()
        conn.close()
        return {"status": "removed", "is_wishlisted": False, "message": "Removed from wishlist"}
    else:
        cursor.execute("INSERT INTO wishlist (user_id, product_id) VALUES (?, ?)", (USER_ID, body.product_id))
        conn.commit()
        conn.close()
        return {"status": "added", "is_wishlisted": True, "message": "Saved to wishlist"}

@router.post("/move-to-cart")
def move_to_cart(body: WishlistToggle):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if in wishlist
    cursor.execute("SELECT id FROM wishlist WHERE user_id = ? AND product_id = ?", (USER_ID, body.product_id))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Item not in wishlist")
        
    # Remove from wishlist
    cursor.execute("DELETE FROM wishlist WHERE user_id = ? AND product_id = ?", (USER_ID, body.product_id))
    
    # Add to cart
    cursor.execute("SELECT quantity FROM cart WHERE user_id = ? AND product_id = ?", (USER_ID, body.product_id))
    row = cursor.fetchone()
    if row:
        cursor.execute("UPDATE cart SET quantity = quantity + 1 WHERE user_id = ? AND product_id = ?", (USER_ID, body.product_id))
    else:
        cursor.execute("INSERT INTO cart (user_id, product_id, quantity) VALUES (?, ?, 1)", (USER_ID, body.product_id))
        
    conn.commit()
    conn.close()
    return {"status": "success", "message": "Moved to cart"}
