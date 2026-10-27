# ⚡ FlashCart - Quick Commerce Web Application

A full-stack, hyper-responsive **10-Minute Quick Commerce** application inspired by Blinkit, Zepto, and Swiggy Instamart.

Built with **FastAPI (Python 3.13)**, **SQLite3**, **Tailwind CSS**, and **Lucide Icons**.

---

## 🌟 Key Features

1. **📦 1,000+ Realistic Products Catalog**:
   - Seeded with **1,050 authentic quick commerce SKUs** across 14 major categories.
   - Indian household staples and favorite brands (Amul, Lay's, Mother Dairy, Maggi, Tata, Fortune, Dettol, Britannia, etc.).
   - Product attributes: MRP, discount %, size/weight units (e.g. 500g, 1L), ratings, reviews, badges, and delivery time tags.

2. **⚡ Ultra-Fast Search & Navigation**:
   - Instant debounced search across titles, brands, and categories.
   - Category capsules (Fresh Produce, Dairy & Eggs, Snacks, Instant Meals, Cold Drinks, Bakery, etc.).
   - Subcategory chips, price sorting, discount sorting, in-stock filter, and **price range filter** (min/max inputs + quick presets like Under ₹50, ₹100–₹250, Above ₹500).

3. **🛒 Cart & Smart Bill Breakdown**:
   - Interactive quantity control (`+` / `-`) on product cards and cart drawer.
   - Floating sticky cart pill on desktop and mobile.
   - Real-time bill calculation: Item Total, Delivery Fee, Handling Fee, Tip Delivery Hero (₹10, ₹20, ₹30), and Coupon Savings.
   - **Coupons supported**:
     - `QUICK100`: Flat ₹100 Off on orders ₹399+
     - `WELCOME50`: Flat ₹50 Off on orders ₹199+
     - `FREEDEL`: Free Delivery fee waiver

4. **❤️ Wishlist**:
   - One-click heart toggle on cards and product quick-view modal.
   - Saved items drawer with "Move to Cart" and item count badge.

5. **⏱️ 10-Minute Live Delivery Tracking**:
   - Real-time animated delivery screen triggered right after order placement.
   - Electric scooter progress bar moving from **Dark Store #104** to customer address.
   - 10-Minute Countdown Clock with live remaining minutes & seconds.
   - 4-Stage timeline (*Order Placed* &rarr; *Packed & Chilled* &rarr; *Out for Delivery* &rarr; *Delivered*).
   - Delivery partner profile (*Rider Name, Electric Vehicle, Rating, Call simulation*).

6. **👛 Quick Wallet & Multi-Payment**:
   - In-app digital wallet with preloaded ₹650.00 balance.
   - Instant wallet top-up (+₹100, +₹250, +₹500, +₹1,000).
   - 1-Click checkout with wallet balance.
   - Multi-payment support: UPI (GPay/PhonePe/Paytm), Credit/Debit Card, and Cash on Delivery (COD).
   - Complete wallet ledger with credit/debit history and reference IDs.

7. **⚙️ Settings & User Management**:
   - User Profile management (Name, Phone, Email).
   - Address Book (Add multiple delivery addresses, set default, delete).
   - Order History with 1-click **Reorder** functionality.
   - Demo phone OTP verification with 1-click auto-fill (`1234`).

---

## 🚀 How to Run

1. Open your terminal in this directory:
   ```bash
   cd C:\Users\bikas\.gemini\antigravity\scratch\quick-commerce-app
   ```

2. Start the application:
   ```bash
   python run.py
   ```

3. Open your browser and navigate to:
   - **Web App**: [http://127.0.0.1:8000](http://127.0.0.1:8000)
   - **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 📂 Project Architecture

```
quick-commerce-app/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI server & route registration
│   ├── database.py          # SQLite schema & DB connection
│   ├── catalog_seed.py      # Seed generator for 1,000+ realistic products
│   ├── models.py            # Pydantic models for validation
│   ├── routes/
│   │   ├── products.py      # Catalog, search, category filters
│   │   ├── cart.py          # Cart management & bill calculation
│   │   ├── wishlist.py      # Wishlist toggle & move to cart
│   │   ├── orders.py        # Checkout & 10-minute live delivery tracker
│   │   ├── wallet.py        # Wallet balance, top-up, & transaction ledger
│   │   └── user.py          # User auth, profile, & address management
│   └── static/
│       ├── index.html       # Single Page Application interface
│       ├── app.js           # Client state, live tracking & Web Audio
│       └── styles.css       # Custom animations & responsive design
├── run.py                   # One-click startup script
├── requirements.txt         # Dependencies
└── README.md                # Documentation
```
