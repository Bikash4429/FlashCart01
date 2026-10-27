import requests
import json
from app.config import QC_API_KEY, QC_BASE_URL, DEFAULT_LAT, DEFAULT_LON
from app.database import get_db_connection

HEADERS = {
    "X-API-Key": QC_API_KEY,
    "Content-Type": "application/json"
}

# Mapping search queries to Quick Commerce categories & subcategories
CATALOG_SYNC_MAP = [
    # (search_term, category, subcategory, platform)
    ("milk", "Dairy, Bread & Eggs", "Milk & Cream", "BlinkIt"),
    ("bread", "Dairy, Bread & Eggs", "Bread & Pav", "BlinkIt"),
    ("butter cheese", "Dairy, Bread & Eggs", "Butter & Cheese", "Zepto"),
    ("eggs", "Dairy, Bread & Eggs", "Eggs", "BlinkIt"),
    ("curd dahi", "Dairy, Bread & Eggs", "Curd & Yogurt", "Zepto"),
    ("chips", "Snacks & Munchies", "Chips & Crisps", "BlinkIt"),
    ("namkeen bhujia", "Snacks & Munchies", "Namkeen & Bhujia", "BlinkIt"),
    ("popcorn nachos", "Snacks & Munchies", "Popcorn & Puffs", "Zepto"),
    ("dry fruits", "Masalas & Dry Fruits", "Dry Fruits & Seeds", "BlinkIt"),
    ("maggi noodles", "Instant & Frozen Food", "Noodles & Pasta", "BlinkIt"),
    ("frozen snacks", "Instant & Frozen Food", "Frozen Snacks", "Zepto"),
    ("coca cola cold drink", "Cold Drinks & Juices", "Soft Drinks", "BlinkIt"),
    ("juice", "Cold Drinks & Juices", "Fruit Juices", "Zepto"),
    ("energy drink", "Cold Drinks & Juices", "Energy Drinks", "BlinkIt"),
    ("biscuits cookies", "Bakery & Biscuits", "Cookies & Biscuits", "BlinkIt"),
    ("tea chai", "Tea, Coffee & Beverages", "Tea Bags & Leaves", "BlinkIt"),
    ("coffee", "Tea, Coffee & Beverages", "Instant Coffee", "Zepto"),
    ("atta flour", "Atta, Rice & Dals", "Flours & Atta", "BlinkIt"),
    ("basmati rice", "Atta, Rice & Dals", "Basmati & Daily Rice", "Zepto"),
    ("dal pulses", "Atta, Rice & Dals", "Lentils & Pulses", "BlinkIt"),
    ("cooking oil ghee", "Atta, Rice & Dals", "Cooking Oils & Ghee", "BlinkIt"),
    ("masala spices", "Masalas & Dry Fruits", "Blended Spices", "BlinkIt"),
    ("vegetables", "Fresh Fruits & Vegetables", "Fresh Vegetables", "BlinkIt"),
    ("fruits", "Fresh Fruits & Vegetables", "Fresh Fruits", "Zepto"),
    ("detergent", "Cleaning & Household", "Laundry & Detergents", "BlinkIt"),
    ("dishwash cleaner", "Cleaning & Household", "Dishwashing", "Zepto"),
    ("soap body wash", "Personal Care", "Soaps & Body Wash", "BlinkIt"),
    ("shampoo conditioner", "Personal Care", "Hair Care", "Zepto"),
    ("toothpaste", "Personal Care", "Oral Hygiene", "BlinkIt"),
    ("baby diapers", "Baby Care", "Diapers & Wipes", "BlinkIt"),
    ("pet dog food", "Pet Supplies", "Dog Food", "BlinkIt"),
    ("wellness pain relief", "Pharma & Wellness", "First Aid & Pain", "BlinkIt")
]

def check_credits():
    """Checks credits remaining on QuickCommerce API (Free endpoint, 0 credits cost)."""
    try:
        url = f"{QC_BASE_URL}/v1/credits"
        res = requests.get(url, headers=HEADERS, timeout=8)
        if res.status_code == 200:
            return res.json()
        return {"error": f"Status {res.status_code}", "detail": res.text}
    except Exception as e:
        return {"error": str(e)}

def search_qc_products(query, platform="BlinkIt", lat=DEFAULT_LAT, lon=DEFAULT_LON):
    """Searches real products via QuickCommerce API from BlinkIt/Zepto/Swiggy."""
    try:
        url = f"{QC_BASE_URL}/v1/search"
        params = {
            "q": query,
            "platform": platform,
            "lat": lat,
            "lon": lon
        }
        res = requests.get(url, headers=HEADERS, params=params, timeout=12)
        if res.status_code == 200:
            return res.json()
        return {"error": f"Status {res.status_code}", "detail": res.text}
    except Exception as e:
        return {"error": str(e)}

def transform_and_save_products(products_data, category, subcategory):
    """Converts QC API product payload into local database records."""
    if not products_data or not isinstance(products_data, list):
        return 0

    conn = get_db_connection()
    cursor = conn.cursor()
    saved_count = 0

    for p in products_data:
        name = p.get("name")
        if not name:
            continue
            
        mrp = float(p.get("mrp") or p.get("offer_price") or 50.0)
        price = float(p.get("offer_price") or p.get("mrp") or 50.0)
        if price > mrp:
            mrp = price
            
        discount_pct = int(round(((mrp - price) / mrp) * 100)) if mrp > 0 and mrp > price else 0
        unit = p.get("quantity") or "1 unit"
        brand = p.get("brand") or "Verified Brand"
        
        # Real platform images from BlinkIt / Zepto CDN
        images = p.get("images") or []
        image_url = images[0] if images else "https://images.unsplash.com/photo-1542838132-92c53300491e?auto=format&fit=crop&w=400&q=80"
        
        rating = round(float(p.get("rating") or 4.5), 1)
        rating_count = int(p.get("rating_count") or 120)
        in_stock = 1 if p.get("available", True) else 0
        
        platform_info = p.get("platform") or {}
        platform_name = platform_info.get("name") or "BlinkIt"
        sla = platform_info.get("sla") or "10 MINS"
        badge = f"{platform_name} · {sla}"
        
        description = f"Fresh and authentic {name} sourced directly via {platform_name} dark store. Delivered in {sla}."
        deeplink = p.get("deeplink") or ""

        # Check if already exists by name
        cursor.execute("SELECT id FROM products WHERE name = ?", (name,))
        existing = cursor.fetchone()
        
        if existing:
            cursor.execute("""
                UPDATE products SET 
                    price = ?, mrp = ?, discount_pct = ?, unit = ?, 
                    image_url = ?, in_stock = ?, delivery_eta = ?, badge = ?, description = ?
                WHERE id = ?
            """, (price, mrp, discount_pct, unit, image_url, in_stock, sla.upper(), badge, description, existing["id"]))
        else:
            cursor.execute("""
                INSERT INTO products (
                    name, brand, category, subcategory, price, mrp, discount_pct,
                    unit, rating, rating_count, image_url, in_stock, delivery_eta, badge, description
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name, brand, category, subcategory, price, mrp, discount_pct,
                unit, rating, rating_count, image_url, in_stock, sla.upper(), badge, description
            ))
            saved_count += 1

    conn.commit()
    conn.close()
    return saved_count

def sync_catalog_with_api(max_terms=18):
    """
    Clears default procedural products and synchronizes real products
    across quick-commerce categories using QuickCommerce API.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. Check if we need to remove procedural products
    print("Clearing default procedural products to replace with live QuickCommerce API data...")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM cart") # Clear cart items referring to deleted IDs
    cursor.execute("DELETE FROM wishlist") # Clear wishlist
    conn.commit()
    conn.close()

    total_synced = 0
    terms_to_run = CATALOG_SYNC_MAP[:max_terms]

    for term, cat, subcat, platform in terms_to_run:
        print(f"Fetching '{term}' from QuickCommerce API ({platform})...")
        res = search_qc_products(query=term, platform=platform)
        
        if "data" in res and "products" in res["data"]:
            prods = res["data"]["products"]
            saved = transform_and_save_products(prods, cat, subcat)
            total_synced += saved
            print(f"  -> Added {saved} real products from {platform} ({len(prods)} returned)")
        else:
            print(f"  -> Warning: {res.get('error', 'No products found for term')}")

    print(f"\nSuccessfully populated database with {total_synced} real products from QuickCommerce API!")
    return total_synced
