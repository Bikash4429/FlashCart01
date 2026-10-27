from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path
from contextlib import asynccontextmanager

from app.database import get_db_connection, init_db
from app.routes import products, cart, wishlist, orders, wallet, user, qc

STATIC_DIR = Path(__file__).resolve().parent / "static"

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    init_db()
    yield
    # Teardown: if any

app = FastAPI(
    title="FlashBlink - Quick Commerce Platform",
    description="Ultra-fast 10-minute grocery delivery powered by QuickCommerce API",
    version="2.1.0",
    lifespan=lifespan
)

# Mount API Routers
app.include_router(products.router)
app.include_router(cart.router)
app.include_router(wishlist.router)
app.include_router(orders.router)
app.include_router(wallet.router)
app.include_router(user.router)
app.include_router(qc.router)

# Mount Static Assets
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/")
def read_root():
    return FileResponse(str(STATIC_DIR / "index.html"))

@app.get("/health")
def health_check():
    return {"status": "online", "platform": "FlashBlink Quick Commerce"}
