from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from app.services.qc_api import check_credits, search_qc_products, transform_and_save_products, sync_catalog_with_api
from app.config import QC_API_KEY, DEFAULT_PLATFORMS, DEFAULT_LAT, DEFAULT_LON
from app.database import get_db_connection

router = APIRouter(prefix="/api/qc", tags=["quickcommerce_api"])

@router.get("/status")
def get_qc_status():
    """Returns QuickCommerce API status, available credits, and connected platforms."""
    credits_info = check_credits()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as count FROM products")
    product_count = cursor.fetchone()["count"]
    conn.close()

    # Mask API key for UI security
    masked_key = f"{QC_API_KEY[:8]}...{QC_API_KEY[-6:]}" if len(QC_API_KEY) > 14 else QC_API_KEY

    return {
        "status": "connected",
        "api_key_configured": bool(QC_API_KEY),
        "masked_api_key": masked_key,
        "default_platforms": DEFAULT_PLATFORMS,
        "location": {"lat": DEFAULT_LAT, "lon": DEFAULT_LON, "city": "Bhubaneswar (Dark Store Hub)"},
        "credits": credits_info,
        "total_products_synced": product_count
    }

@router.get("/search")
def live_qc_search(
    q: str = Query(..., description="Product search term"),
    platform: str = Query("BlinkIt", description="BlinkIt, Zepto, Swiggy, BigBasket, etc."),
    lat: float = Query(DEFAULT_LAT),
    lon: float = Query(DEFAULT_LON),
    category: Optional[str] = "Snacks & Munchies",
    subcategory: Optional[str] = "Chips & Crisps"
):
    """Executes a real-time live product search via QuickCommerce API and caches results."""
    res = search_qc_products(query=q, platform=platform, lat=lat, lon=lon)
    if "error" in res:
        raise HTTPException(status_code=502, detail=res["error"])
        
    prods = res.get("data", {}).get("products", [])
    saved = transform_and_save_products(prods, category, subcategory)
    
    return {
        "query": q,
        "platform": platform,
        "total_results": len(prods),
        "saved_to_catalog": saved,
        "credits_remaining": res.get("credits_remaining"),
        "products": prods
    }

@router.post("/sync")
def trigger_sync(max_terms: int = Query(10, ge=1, le=30)):
    """Triggers sync of real items across categories from QuickCommerce API."""
    count = sync_catalog_with_api(max_terms=max_terms)
    return {
        "status": "success",
        "message": f"Successfully synchronized {count} real products from QuickCommerce API",
        "products_synced": count
    }
