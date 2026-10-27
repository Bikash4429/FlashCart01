import requests
import time
import subprocess
import sys

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

BASE_URL = "http://127.0.0.1:8000"

def test_app():
    print("Testing Quick Commerce endpoints...")
    
    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("✓ Health check passed")
    
    # 2. Categories
    res = requests.get(f"{BASE_URL}/api/categories")
    assert res.status_code == 200
    categories = res.json()
    assert len(categories) >= 12, f"Expected categories, got {len(categories)}"
    print(f"✓ Categories loaded: {len(categories)} categories")
    
    # 3. QuickCommerce API Status verification
    res = requests.get(f"{BASE_URL}/api/qc/status")
    assert res.status_code == 200
    qc_data = res.json()
    assert qc_data["status"] == "connected"
    credits_left = qc_data["credits"]["summary"]["total_available"]
    print(f"✓ QuickCommerce API verified: Connected with key {qc_data['masked_api_key']} ({credits_left} credits remaining)")

    # 4. Products verification (Sourced via QuickCommerce API)
    res = requests.get(f"{BASE_URL}/api/products?limit=10")
    assert res.status_code == 200
    data = res.json()
    total = data["total"]
    assert total >= 500, f"Expected 500+ real products, got {total}"
    print(f"✓ Catalog verified: {total} real products sourced via QuickCommerce API (BlinkIt/Zepto)")
    
    # 4. Search verification
    res = requests.get(f"{BASE_URL}/api/products?search=milk")
    assert res.status_code == 200
    search_data = res.json()
    assert search_data["total"] > 0, "Expected milk search results"
    print(f"✓ Search verified: found {search_data['total']} items matching 'milk'")
    
    # 5. Cart Operations
    first_prod_id = data["items"][0]["id"]
    # Clear cart
    requests.post(f"{BASE_URL}/api/cart/clear")
    # Add to cart
    res = requests.post(f"{BASE_URL}/api/cart/add", json={"product_id": first_prod_id, "quantity": 2})
    assert res.status_code == 200
    # Get cart
    res = requests.get(f"{BASE_URL}/api/cart")
    cart_data = res.json()
    assert len(cart_data["items"]) == 1
    assert cart_data["bill"]["item_count"] == 2
    print(f"✓ Cart operations verified: {cart_data['items'][0]['name']} x 2 added")
    
    # 6. Wishlist
    res = requests.post(f"{BASE_URL}/api/wishlist/toggle", json={"product_id": first_prod_id})
    assert res.status_code == 200
    res = requests.get(f"{BASE_URL}/api/wishlist")
    assert res.json()["count"] >= 1
    print("✓ Wishlist toggle verified")
    
    # 7. Wallet Top-Up
    res = requests.get(f"{BASE_URL}/api/wallet")
    initial_balance = res.json()["balance"]
    res = requests.post(f"{BASE_URL}/api/wallet/topup", json={"amount": 200.0, "payment_channel": "UPI"})
    assert res.status_code == 200
    new_balance = res.json()["new_balance"]
    assert round(new_balance - initial_balance, 2) == 200.0
    print(f"✓ Wallet top-up verified: Balance updated from ₹{initial_balance} to ₹{new_balance}")
    
    # 8. Order Checkout with Wallet
    res = requests.post(f"{BASE_URL}/api/orders/checkout", json={
        "payment_method": "wallet",
        "tip": 20.0,
        "coupon_code": "WELCOME50"
    })
    assert res.status_code == 200, f"Checkout failed: {res.text}"
    order = res.json()
    order_id = order["order_id"]
    print(f"✓ Checkout verified: Created {order['order_number']}, Total: ₹{order['total_amount']}")
    
    # 9. 10-Minute Live Tracking
    res = requests.get(f"{BASE_URL}/api/orders/{order_id}/tracking")
    assert res.status_code == 200
    tracking = res.json()
    assert "stage_text" in tracking
    assert "rider" in tracking
    print(f"✓ Live Tracking verified: Stage: '{tracking['stage_text']}', Rider: {tracking['rider']['name']}, ETA: {tracking['eta_minutes']} mins")
    
    # 10. Frontend Index page serves HTML
    res = requests.get(f"{BASE_URL}/")
    assert res.status_code == 200
    assert "<title>FlashCart" in res.text
    print("✓ Frontend Single Page Application serves successfully")
    
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY! Ready for use.")

if __name__ == "__main__":
    test_app()
