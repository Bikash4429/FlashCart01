import os
import sys
import uvicorn
from pathlib import Path

# Configure UTF-8 encoding for Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))

def main():
    print("=" * 65)
    print("  [FlashCart] Ultra-Fast Quick Commerce Platform")
    print("  [Catalog] Powered by QuickCommerce API (BlinkIt, Zepto, Swiggy)")
    print("  [Delivery] 10-Minute Dark Store Delivery Simulator")
    print("=" * 65)
    print("  🚀 Starting server at: http://127.0.0.1:8000")
    print("  📖 API Documentation:  http://127.0.0.1:8000/docs")
    print("=" * 65)
    
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)

if __name__ == "__main__":
    main()
