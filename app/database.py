import sqlite3
import os
from pathlib import Path

DB_DIR = Path(__file__).resolve().parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)
DB_PATH = DB_DIR / "quickcommerce.db"

def get_db_connection():
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        phone TEXT UNIQUE,
        name TEXT,
        email TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS addresses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        tag TEXT DEFAULT 'Home',
        address_line TEXT NOT NULL,
        landmark TEXT,
        city TEXT DEFAULT 'New Delhi',
        pincode TEXT DEFAULT '110001',
        is_default INTEGER DEFAULT 0,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT,
        category TEXT NOT NULL,
        subcategory TEXT NOT NULL,
        price REAL NOT NULL,
        mrp REAL NOT NULL,
        discount_pct INTEGER DEFAULT 0,
        unit TEXT NOT NULL,
        rating REAL DEFAULT 4.5,
        rating_count INTEGER DEFAULT 120,
        image_url TEXT,
        in_stock INTEGER DEFAULT 1,
        delivery_eta TEXT DEFAULT '10 MINS',
        badge TEXT,
        description TEXT
    );

    CREATE INDEX IF NOT EXISTS idx_products_category ON products(category);
    CREATE INDEX IF NOT EXISTS idx_products_subcategory ON products(subcategory);
    CREATE INDEX IF NOT EXISTS idx_products_name ON products(name);

    CREATE TABLE IF NOT EXISTS cart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        product_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, product_id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS wishlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        product_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, product_id),
        FOREIGN KEY (product_id) REFERENCES products(id)
    );

    CREATE TABLE IF NOT EXISTS wallets (
        user_id INTEGER PRIMARY KEY,
        balance REAL DEFAULT 500.0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS wallet_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL, -- 'credit' or 'debit'
        title TEXT NOT NULL,
        reference_id TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE NOT NULL,
        user_id INTEGER NOT NULL,
        item_total REAL NOT NULL,
        delivery_fee REAL NOT NULL DEFAULT 0,
        handling_fee REAL NOT NULL DEFAULT 5,
        tip REAL NOT NULL DEFAULT 0,
        discount REAL NOT NULL DEFAULT 0,
        coupon_code TEXT,
        total_amount REAL NOT NULL,
        payment_method TEXT NOT NULL,
        payment_status TEXT NOT NULL DEFAULT 'completed',
        order_status TEXT NOT NULL DEFAULT 'placed',
        delivery_address_snapshot TEXT,
        rider_name TEXT DEFAULT 'Vikram Sharma',
        rider_phone TEXT DEFAULT '+91 98765 43210',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    );

    CREATE TABLE IF NOT EXISTS order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        product_id INTEGER NOT NULL,
        product_name TEXT NOT NULL,
        price REAL NOT NULL,
        quantity INTEGER NOT NULL,
        unit TEXT NOT NULL,
        image_url TEXT,
        FOREIGN KEY (order_id) REFERENCES orders(id)
    );
    """)

    # Seed default user if not exists
    cursor.execute("SELECT id FROM users WHERE id = 1")
    if not cursor.fetchone():
        cursor.execute("""
            INSERT INTO users (id, phone, name, email) 
            VALUES (1, '9876543210', 'Alex Johnson', 'alex.quick@gmail.com')
        """)
        # Seed default addresses
        cursor.execute("""
            INSERT INTO addresses (user_id, tag, address_line, landmark, city, pincode, is_default)
            VALUES 
            (1, 'Home', 'Flat 402, Sunshine Towers, Park Avenue', 'Opposite Metro Station', 'Bhubaneswar', '751001', 1),
            (1, 'Work', 'Tower B, 7th Floor, Cyber Tech Hub', 'Near Tech Gate 2', 'Bhubaneswar', '751024', 0)
        """)
        # Seed wallet with welcome bonus
        cursor.execute("""
            INSERT INTO wallets (user_id, balance) VALUES (1, 650.0)
        """)
        cursor.execute("""
            INSERT INTO wallet_transactions (user_id, amount, type, title, reference_id)
            VALUES 
            (1, 500.0, 'credit', 'Welcome Bonus Credited', 'BONUS-500'),
            (1, 150.0, 'credit', 'Cashback on First Sign-in', 'CB-150')
        """)

    conn.commit()
    conn.close()
