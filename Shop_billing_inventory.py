
import sqlite3
import datetime
from decimal import Decimal, ROUND_HALF_UP
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

DB = "shop.db"

def money(x):
    return f"₹{Decimal(x).quantize(Decimal('0.01'), ROUND_HALF_UP)}"

def init_db():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS products (sku TEXT PRIMARY KEY, name TEXT, price REAL, stock INT)")
    c.execute("CREATE TABLE IF NOT EXISTS bills (id INTEGER PRIMARY KEY, date TEXT, total REAL, items TEXT)")
    conn.commit()
    conn.close()

def add_product():
    sku = input("SKU: ").strip()
    name = input("Name: ").strip()
    price = float(input("Price: "))
    stock = int(input("Stock: "))
    conn = sqlite3.connect(DB)
    try:
        conn.execute("INSERT INTO products VALUES (?,?,?,?)", (sku, name, price, stock))
        conn.commit()
        print(f"✓ Added {name}")
    except sqlite3.IntegrityError:
        print("✗ SKU exists")
    conn.close()

def list_products():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT * FROM products ORDER BY name").fetchall()
    conn.close()
    if not rows:
        print("No products")
        return
    print("\n" + "-"*60)
    print(f"{'SKU':<10} {'Name':<25} {'Price':>10} {'Stock':>8}")
    print("-"*60)
    for sku, name, price, stock in rows:
        flag = " ⚠" if stock < 5 else ""
        print(f"{sku:<10} {name:<25} {money(price):>10} {stock:>8}{flag}")
    print("-"*60)

def update_stock():
    sku = input("SKU: ").strip()
    qty = int(input("Change (+/-): "))
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT stock FROM products WHERE sku=?", (sku,))
    row = c.fetchone()
    if not row:
        print("✗ Not found")
        conn.close()
        return
    new_stock = row[0] + qty
    if new_stock < 0:
        print("✗ Stock can't be negative")
        conn.close()
        return
    c.execute("UPDATE products SET stock=? WHERE sku=?", (new_stock, sku))
    conn.commit()
    conn.close()
    print(f"✓ Stock updated: {row[0]} → {new_stock}")

def create_bill():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    items = []
    print("\nAdd items (type 'done' to finish)")
    
    while True:
        sku = input("SKU: ").strip()
        if sku.lower() == 'done':
            break
        c.execute("SELECT name, price, stock FROM products WHERE sku=?", (sku,))
        row = c.fetchone()
        if not row:
            print("✗ Not found")
            continue
        name, price, stock = row
        qty = int(input(f"Qty (max {stock}): "))
        if qty <= 0 or qty > stock:
            print("✗ Invalid quantity")
            continue
        items.append((sku, name, qty, price))
        c.execute("UPDATE products SET stock=stock-? WHERE sku=?", (qty, sku))
        print(f"✓ Added {qty}x {name}")
    
    if not items:
        print("No items")
        conn.close()
        return
    
    total = sum(q * p for _, _, q, p in items)
    date = datetime.datetime.now().isoformat()
    items_str = ";".join(f"{s}:{n}:{q}:{p}" for s, n, q, p in items)
    
    c.execute("INSERT INTO bills (date, total, items) VALUES (?,?,?)", (date, total, items_str))
    bill_id = c.lastrowid
    conn.commit()
    conn.close()
    
    print(f"\n✓ Bill #{bill_id} | Total: {money(total)}")
    generate_pdf(bill_id, date, items, total)
    print(f"✓ Invoice saved: invoice_{bill_id}.pdf")

def generate_pdf(bill_id, date, items, total):
    c = canvas.Canvas(f"invoice_{bill_id}.pdf", pagesize=A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 800, "INVOICE")
    c.setFont("Helvetica", 10)
    c.drawString(50, 780, f"Bill #{bill_id}")
    c.drawString(50, 765, f"Date: {datetime.datetime.fromisoformat(date).strftime('%Y-%m-%d %H:%M')}")
    
    y = 730
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Item")
    c.drawString(300, y, "Qty")
    c.drawString(380, y, "Price")
    c.drawString(480, y, "Total")
    y -= 20
    
    c.setFont("Helvetica", 10)
    for sku, name, qty, price in items:
        c.drawString(50, y, name[:30])
        c.drawString(300, y, str(qty))
        c.drawString(380, y, money(price))
        c.drawString(480, y, money(qty * price))
        y -= 18
    
    y -= 20
    c.setFont("Helvetica-Bold", 12)
    c.drawString(380, y, "TOTAL:")
    c.drawString(480, y, money(total))
    c.save()

def view_bills():
    conn = sqlite3.connect(DB)
    rows = conn.execute("SELECT id, date, total FROM bills ORDER BY id DESC LIMIT 10").fetchall()
    conn.close()
    if not rows:
        print("No bills")
        return
    print("\n" + "-"*60)
    print(f"{'Bill':<8} {'Date':<25} {'Total':>15}")
    print("-"*60)
    for bid, date, total in rows:
        dt = datetime.datetime.fromisoformat(date).strftime('%Y-%m-%d %H:%M')
        print(f"{bid:<8} {dt:<25} {money(total):>15}")
    print("-"*60)

def seed_data():
    conn = sqlite3.connect(DB)
    try:
        demo = [
            ("P001", "Notebook", 50.0, 30),
            ("P002", "Pen", 15.0, 100),
            ("P003", "Water Bottle", 35.0, 50),
        ]
        conn.executemany("INSERT INTO products VALUES (?,?,?,?)", demo)
        conn.commit()
        print("✓ Demo data loaded")
    except sqlite3.IntegrityError:
        print("✗ Data already exists")
    conn.close()

def menu():
    init_db()
    print("\n=== Smart Inventory System ===")
    print("VIT Bhopal | Prabhash Chaturvedi (25BCE10797)")
    
    while True:
        print("\n1. Add Product  2. List Products  3. Update Stock")
        print("4. Create Bill  5. View Bills     6. Seed Demo")
        print("0. Exit")
        
        choice = input("\nChoice: ").strip()
        
        if choice == "1":
            add_product()
        elif choice == "2":
            list_products()
        elif choice == "3":
            update_stock()
        elif choice == "4":
            create_bill()
        elif choice == "5":
            view_bills()
        elif choice == "6":
            seed_data()
        elif choice == "0":
            print("Goodbye! 👋")
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    menu()
