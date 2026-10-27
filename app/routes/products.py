from fastapi import APIRouter, Query, HTTPException
from typing import Optional, List
from app.database import get_db_connection

router = APIRouter(prefix="/api", tags=["products"])

@router.get("/categories")
def get_categories():
    """Returns list of distinct categories and subcategories with count of items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT category, subcategory, COUNT(*) as count 
        FROM products 
        GROUP BY category, subcategory 
        ORDER BY category, subcategory
    """)
    rows = cursor.fetchall()
    
    categories_dict = {}
    for row in rows:
        cat = row["category"]
        subcat = row["subcategory"]
        count = row["count"]
        if cat not in categories_dict:
            categories_dict[cat] = {
                "name": cat,
                "total_items": 0,
                "subcategories": []
            }
        categories_dict[cat]["total_items"] += count
        categories_dict[cat]["subcategories"].append({"name": subcat, "count": count})
    
    conn.close()
    return list(categories_dict.values())

@router.get("/products")
def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(24, ge=1, le=100),
    category: Optional[str] = None,
    subcategory: Optional[str] = None,
    search: Optional[str] = None,
    sort_by: Optional[str] = "popular",
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock_only: Optional[bool] = False
):
    """Paginated, filtered and searchable product listing across 1000+ items."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    conditions = []
    params = []
    
    if category and category.lower() != "all":
        conditions.append("category = ?")
        params.append(category)
        
    if subcategory and subcategory.lower() != "all":
        conditions.append("subcategory = ?")
        params.append(subcategory)
        
    if search and search.strip():
        search_terms = search.strip().split()
        search_clauses = []
        for term in search_terms:
            search_clauses.append("(name LIKE ? OR brand LIKE ? OR category LIKE ? OR subcategory LIKE ?)")
            term_like = f"%{term}%"
            params.extend([term_like, term_like, term_like, term_like])
        conditions.append(" AND ".join(search_clauses))
        
    if min_price is not None:
        conditions.append("price >= ?")
        params.append(min_price)
        
    if max_price is not None:
        conditions.append("price <= ?")
        params.append(max_price)
        
    if in_stock_only:
        conditions.append("in_stock = 1")
        
    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    
    # Sort order
    order_clause = "ORDER BY rating DESC, rating_count DESC" # default popular
    if sort_by == "price_asc":
        order_clause = "ORDER BY price ASC"
    elif sort_by == "price_desc":
        order_clause = "ORDER BY price DESC"
    elif sort_by == "discount":
        order_clause = "ORDER BY discount_pct DESC"
    elif sort_by == "rating":
        order_clause = "ORDER BY rating DESC"
        
    # Count query
    count_query = f"SELECT COUNT(*) as total FROM products {where_clause}"
    cursor.execute(count_query, params)
    total_count = cursor.fetchone()["total"]
    
    # If search term yielded 0 results, query QuickCommerce API live!
    if total_count == 0 and search and search.strip():
        try:
            from app.services.qc_api import search_qc_products, transform_and_save_products
            clean_q = search.strip()
            qc_res = search_qc_products(query=clean_q, platform="BlinkIt")
            if "data" in qc_res and "products" in qc_res["data"]:
                prods = qc_res["data"]["products"]
                if prods:
                    inferred_cat = category if category and category.lower() != "all" else "Snacks & Munchies"
                    inferred_sub = subcategory if subcategory and subcategory.lower() != "all" else "Popular"
                    transform_and_save_products(prods, inferred_cat, inferred_sub)
                    # Re-run count
                    cursor.execute(count_query, params)
                    total_count = cursor.fetchone()["total"]
        except Exception as e:
            print(f"QuickCommerce API live search fallback note: {e}")

    # Items query
    offset = (page - 1) * limit
    items_query = f"SELECT * FROM products {where_clause} {order_clause} LIMIT ? OFFSET ?"
    cursor.execute(items_query, params + [limit, offset])
    rows = cursor.fetchall()
    
    products = [dict(row) for row in rows]
    total_pages = (total_count + limit - 1) // limit if total_count > 0 else 1
    
    conn.close()
    return {
        "items": products,
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

@router.get("/products/featured")
def get_featured_products():
    """Featured deals, bestsellers, and trending picks for the home showcase."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM products 
        WHERE discount_pct >= 20 AND in_stock = 1 
        ORDER BY discount_pct DESC, rating DESC 
        LIMIT 12
    """)
    super_savers = [dict(r) for r in cursor.fetchall()]
    
    cursor.execute("""
        SELECT * FROM products 
        WHERE rating >= 4.7 AND in_stock = 1 
        ORDER BY rating_count DESC 
        LIMIT 12
    """)
    bestsellers = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        "super_savers": super_savers,
        "bestsellers": bestsellers
    }

@router.get("/products/{product_id}")
def get_product_details(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")
    
    product = dict(row)
    # Also fetch similar products
    cursor.execute("""
        SELECT * FROM products 
        WHERE category = ? AND id != ? 
        LIMIT 6
    """, (product["category"], product_id))
    similar = [dict(r) for r in cursor.fetchall()]
    
    conn.close()
    return {
        "product": product,
        "similar": similar
    }
