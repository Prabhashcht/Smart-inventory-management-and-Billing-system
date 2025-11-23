# Pseudo Code & Algorithm Documentation

## Smart Inventory & Billing System

---

## Table of Contents

1. [Main Program Flow](#main-program-flow)
2. [Function Pseudo Codes](#function-pseudo-codes)
3. [Algorithm Explanations](#algorithm-explanations)
4. [Data Processing Flows](#data-processing-flows)
5. [State Machines](#state-machines)

---

## Main Program Flow

```
START PROGRAM
    ↓
INITIALIZE DATABASE
    ├─ Check if shop.db exists
    └─ Create tables if not exist
    ↓
DISPLAY WELCOME MESSAGE
    ├─ Show project title
    ├─ Show student info
    └─ Show institution info
    ↓
┌─ MAIN MENU LOOP ──────────────┐
│                               │
│ DISPLAY MENU OPTIONS          │
│ "1. Add Product"              │
│ "2. List Products"            │
│ "3. Update Stock"             │
│ "4. Create Bill"              │
│ "5. View Bills"               │
│ "6. Seed Demo"                │
│ "0. Exit"                     │
│                               │
│ GET USER CHOICE               │
│                               │
│ IF choice == "0":             │
│   └─ BREAK (EXIT LOOP)        │
│ ELSE:                         │
│   └─ CALL CORRESPONDING       │
│       FUNCTION                │
│                               │
└───────────────────────────────┘
    ↓
DISPLAY GOODBYE MESSAGE
    ↓
END PROGRAM
```

---

## Function Pseudo Codes

### Function: money(x)
**Purpose:** Format number as Indian Rupee currency

```pseudocode
FUNCTION money(x)
    INPUT: x (float or numeric value)
    OUTPUT: String with currency format
    
    PROCESS:
        1. Convert x to Decimal (precise arithmetic)
        2. Round to 2 decimal places (ROUND_HALF_UP)
        3. Prepend Indian Rupee symbol (₹)
        4. Return formatted string
    
    EXAMPLE:
        money(1234.567) → "₹1234.57"
        money(50.0)    → "₹50.00"
        money(0.1)     → "₹0.10"
END FUNCTION
```

### Function: init_db()
**Purpose:** Initialize SQLite database and create tables

```pseudocode
FUNCTION init_db()
    INPUT: None
    OUTPUT: None (Side effect: creates database)
    
    PROCESS:
        1. OPEN connection to "shop.db"
        2. GET database cursor
        3. CREATE TABLE products IF NOT EXISTS:
           - sku (TEXT, PRIMARY KEY)
           - name (TEXT)
           - price (REAL)
           - stock (INTEGER)
        4. CREATE TABLE bills IF NOT EXISTS:
           - id (INTEGER PRIMARY KEY AUTOINCREMENT)
           - date (TEXT)
           - total (REAL)
           - items (TEXT)
        5. COMMIT changes
        6. CLOSE connection
    
    NOTES:
        - IF tables already exist: no error
        - Creates database file if missing
        - Returns immediately if already initialized
END FUNCTION
```

### Function: add_product()
**Purpose:** Add new product to inventory

```pseudocode
FUNCTION add_product()
    INPUT: User input (interactive)
    OUTPUT: None (Side effect: inserts product)
    
    PROCESS:
        1. PROMPT user for SKU
            INPUT → sku
        2. PROMPT user for Name
            INPUT → name
        3. PROMPT user for Price
            INPUT → price
        4. PROMPT user for Stock
            INPUT → stock
        
        5. OPEN database connection
        
        6. TRY:
             EXECUTE: INSERT INTO products VALUES (sku, name, price, stock)
             COMMIT
             DISPLAY "✓ Added {name}"
           CATCH sqlite3.IntegrityError:
             DISPLAY "✗ SKU exists"
           FINALLY:
             CLOSE connection
    
    VALIDATION:
        - SKU must be unique (primary key constraint)
        - Price and stock must be numeric
        - If any error: transaction rolled back
END FUNCTION
```

### Function: list_products()
**Purpose:** Display all products in formatted table

```pseudocode
FUNCTION list_products()
    INPUT: None
    OUTPUT: Console display
    
    PROCESS:
        1. OPEN database connection
        
        2. EXECUTE: SELECT * FROM products ORDER BY name
        
        3. FETCH all results
           products = [list of all products]
        
        4. CLOSE connection
        
        5. IF products is empty:
             DISPLAY "No products"
             RETURN
           END IF
        
        6. DISPLAY table header:
           "SKU | Name | Price | Stock"
        
        7. FOR EACH product IN products:
             sku, name, price, stock = product
             
             IF stock < 5:
                 warning = " ⚠"
             ELSE:
                 warning = ""
             END IF
             
             DISPLAY formatted row:
               sku (left-align 10 chars)
               name (left-align 25 chars)
               money(price) (right-align 10 chars)
               stock (right-align 8 chars)
               warning
        
        8. DISPLAY table footer (separator line)
    
    OUTPUT EXAMPLE:
        ────────────────────────────────────────────
        SKU        Name                     Price   Stock
        ────────────────────────────────────────────
        P001       Notebook                 ₹50.00    30
        P002       Pen                      ₹15.00   100 ⚠
        ────────────────────────────────────────────
END FUNCTION
```

### Function: update_stock()
**Purpose:** Adjust product stock quantity

```pseudocode
FUNCTION update_stock()
    INPUT: User input (interactive)
    OUTPUT: None (Side effect: updates database)
    
    PROCESS:
        1. PROMPT user for SKU
            INPUT → sku
        
        2. PROMPT user for Quantity Change
            INPUT → qty_change (can be positive or negative)
        
        3. OPEN database connection
           GET cursor
        
        4. EXECUTE: SELECT stock FROM products WHERE sku = ?
           result = FETCH result
        
        5. IF result is NULL:
             DISPLAY "✗ Not found"
             CLOSE connection
             RETURN
           END IF
        
        6. old_stock = result[0]
        
        7. new_stock = old_stock + qty_change
        
        8. IF new_stock < 0:
             DISPLAY "✗ Stock can't be negative"
             CLOSE connection
             RETURN
           END IF
        
        9. EXECUTE: UPDATE products SET stock = ? WHERE sku = ?
           (Parameters: new_stock, sku)
        
        10. COMMIT transaction
        
        11. CLOSE connection
        
        12. DISPLAY "✓ Stock updated: {old_stock} → {new_stock}"
    
    VALIDATION:
        - Result cannot be negative
        - SKU must exist
        - Input must be numeric
END FUNCTION
```

### Function: create_bill()
**Purpose:** Create bill and process checkout

```pseudocode
FUNCTION create_bill()
    INPUT: User input (interactive)
    OUTPUT: None (Side effects: inserts bill, updates stock, creates PDF)
    
    PROCESS:
        1. OPEN database connection
        2. items = EMPTY_LIST
        
        3. DISPLAY "Add items (type 'done' to finish)"
        
        4. REPEAT UNTIL user enters 'done':
             PROMPT "SKU: "
             INPUT → sku
             
             IF sku.lower() == 'done':
                 BREAK from loop
             END IF
             
             EXECUTE: SELECT name, price, stock FROM products WHERE sku = ?
             result = FETCH result
             
             IF result is NULL:
                 DISPLAY "✗ Not found"
                 CONTINUE to next iteration
             END IF
             
             name, price, stock = result
             
             PROMPT "Qty (max {stock}): "
             INPUT → qty
             
             IF qty <= 0 OR qty > stock:
                 DISPLAY "✗ Invalid quantity"
                 CONTINUE to next iteration
             END IF
             
             APPEND (sku, name, qty, price) TO items
             
             EXECUTE: UPDATE products SET stock = stock - ? WHERE sku = ?
             (Parameters: qty, sku)
             
             DISPLAY "✓ Added {qty}x {name}"
           END REPEAT
        
        5. IF items is empty:
             DISPLAY "No items"
             CLOSE connection
             RETURN
           END IF
        
        6. total = 0
           FOR EACH item IN items:
               sku, name, qty, price = item
               total = total + (qty * price)
           END FOR
        
        7. date = CURRENT_DATETIME in ISO format
        
        8. items_string = SERIALIZE items to STRING
           Format: "SKU1:Name1:Qty1:Price1;SKU2:Name2:Qty2:Price2;..."
        
        9. EXECUTE: INSERT INTO bills (date, total, items) VALUES (?, ?, ?)
           (Parameters: date, total, items_string)
        
        10. bill_id = GET LAST INSERTED ROW ID
        
        11. COMMIT all changes
        
        12. CLOSE connection
        
        13. DISPLAY "✓ Bill #{bill_id} | Total: {money(total)}"
        
        14. CALL generate_pdf(bill_id, date, items, total)
        
        15. DISPLAY "✓ Invoice saved: invoice_{bill_id}.pdf"
    
    VALIDATION:
        - All stock checks performed
        - Negative quantities rejected
        - Overselling prevented
        - Transactions are atomic (all or nothing)
END FUNCTION
```

### Function: generate_pdf(bill_id, date, items, total)
**Purpose:** Generate PDF invoice

```pseudocode
FUNCTION generate_pdf(bill_id, date, items, total)
    INPUT: 
        - bill_id (integer)
        - date (ISO string)
        - items (list of tuples)
        - total (float)
    OUTPUT: None (Side effect: creates PDF file)
    
    PROCESS:
        1. filename = "invoice_{bill_id}.pdf"
        
        2. CREATE canvas object
           canvas = Canvas(filename, A4_PAGE_SIZE)
        
        3. DRAW HEADER:
           SET font to Helvetica-Bold, size 16
           DRAW text "INVOICE" at position (50, 800)
           
           SET font to Helvetica, size 10
           DRAW text "Bill #{bill_id}" at (50, 780)
           
           parsed_date = PARSE ISO date string
           formatted_date = FORMAT date as "YYYY-MM-DD HH:MM"
           DRAW text "Date: {formatted_date}" at (50, 765)
        
        4. DRAW TABLE HEADER at y=730:
           SET font to Helvetica-Bold, size 10
           DRAW "Item" at x=50
           DRAW "Qty" at x=300
           DRAW "Price" at x=380
           DRAW "Total" at x=480
           
           y_position = 730 - 20
        
        5. DRAW TABLE ROWS:
           SET font to Helvetica, size 10
           
           FOR EACH item IN items:
               sku, name, qty, price = item
               item_total = qty * price
               
               DRAW TRUNCATE(name, 30) at (50, y_position)
               DRAW STR(qty) at (300, y_position)
               DRAW money(price) at (380, y_position)
               DRAW money(item_total) at (480, y_position)
               
               y_position = y_position - 18
           END FOR
        
        6. DRAW TOTALS:
           y_position = y_position - 20
           
           SET font to Helvetica-Bold, size 12
           DRAW "TOTAL:" at (380, y_position)
           DRAW money(total) at (480, y_position)
        
        7. SAVE canvas to file
           canvas.save()
    
    OUTPUT FILE:
        Location: Current directory
        Filename: invoice_{bill_id}.pdf
        Format: PDF document
        Size: ~50-100 KB
END FUNCTION
```

### Function: view_bills()
**Purpose:** Display recent bills

```pseudocode
FUNCTION view_bills()
    INPUT: None
    OUTPUT: Console display
    
    PROCESS:
        1. OPEN database connection
        
        2. EXECUTE: SELECT id, date, total FROM bills ORDER BY id DESC LIMIT 10
        
        3. results = FETCH all results
        
        4. CLOSE connection
        
        5. IF results is empty:
             DISPLAY "No bills"
             RETURN
           END IF
        
        6. DISPLAY table header and separator
           "Bill | Date | Total"
        
        7. FOR EACH bill IN results (last 10 in reverse order):
             bill_id, date_iso, total = bill
             
             parsed_date = PARSE ISO format date
             formatted = FORMAT date as "YYYY-MM-DD HH:MM"
             
             DISPLAY formatted row:
               bill_id (left 8 chars)
               formatted (25 chars)
               money(total) (right aligned)
        
        8. DISPLAY table footer (separator)
END FUNCTION
```

### Function: seed_data()
**Purpose:** Load demo products

```pseudocode
FUNCTION seed_data()
    INPUT: None
    OUTPUT: None (Side effect: populates database)
    
    PROCESS:
        1. OPEN database connection
        
        2. demo_products = [
             ("P001", "Notebook", 50.0, 30),
             ("P002", "Pen", 15.0, 100),
             ("P003", "Water Bottle", 35.0, 50)
           ]
        
        3. TRY:
             FOR EACH product IN demo_products:
                 EXECUTE: INSERT INTO products VALUES (product)
             END FOR
             
             COMMIT transaction
             DISPLAY "✓ Demo data loaded"
        
           CATCH sqlite3.IntegrityError:
             DISPLAY "✗ Data already exists"
        
           FINALLY:
             CLOSE connection
    
    NOTES:
        - Only works if products table is empty
        - Used for initial testing
        - Contains 3 sample products
END FUNCTION
```

### Function: menu()
**Purpose:** Main application loop

```pseudocode
FUNCTION menu()
    INPUT: None
    OUTPUT: Program execution
    
    PROCESS:
        1. CALL init_db()
        
        2. DISPLAY header:
           "=== Smart Inventory System ==="
           "VIT Bhopal | Prabhash Chaturvedi (25BCE10797)"
        
        3. INFINITE LOOP:
             DISPLAY menu options:
             "1. Add Product"
             "2. List Products"
             "3. Update Stock"
             "4. Create Bill"
             "5. View Bills"
             "6. Seed Demo"
             "0. Exit"
             
             PROMPT "Choice: "
             INPUT → user_choice
             
             SWITCH user_choice:
                 CASE "1":
                     CALL add_product()
                 CASE "2":
                     CALL list_products()
                 CASE "3":
                     CALL update_stock()
                 CASE "4":
                     CALL create_bill()
                 CASE "5":
                     CALL view_bills()
                 CASE "6":
                     CALL seed_data()
                 CASE "0":
                     DISPLAY "Goodbye! 👋"
                     BREAK (exit loop)
                 DEFAULT:
                     DISPLAY "Invalid choice"
             END SWITCH
           END LOOP
    
    PROGRAM ENDS
END FUNCTION
```

---

## Algorithm Explanations

### Algorithm 1: Stock Validation

```
Purpose: Ensure stock availability before billing

Algorithm:
    FOR EACH item requested:
        qty_requested = read from user
        
        IF qty_requested <= 0:
            REJECT with "Qty must be > 0"
        
        available = query database for SKU
        
        IF qty_requested > available:
            REJECT with "Not enough stock"
        ELSE:
            ACCEPT item
            UPDATE database: stock -= qty_requested
    
Complexity: O(n) where n = number of items
Performance: <100ms for typical bill (5-10 items)
```

### Algorithm 2: Currency Formatting

```
Purpose: Ensure precise financial calculations

Algorithm:
    input_value (float)
        ↓
    Decimal(input_value) — Convert to exact decimal
        ↓
    quantize(Decimal('0.01'), ROUND_HALF_UP) — Round to 2 places
        ↓
    f"₹{result}" — Format with currency symbol
        ↓
    return formatted_string

Why Decimal?
- Float has precision errors (e.g., 0.1 + 0.2 ≠ 0.3)
- Financial calculations require precision
- Decimal provides exact arithmetic
```

### Algorithm 3: Low-Stock Warning

```
Purpose: Identify products needing reorder

Algorithm:
    THRESHOLD = 5 (configurable)
    
    FOR EACH product in products_table:
        IF product.stock <= THRESHOLD:
            ADD warning flag (⚠)
    
    DISPLAY products with warning flags

Result: Quick visual indication for shop owner
```

### Algorithm 4: Bill Item Parsing

```
Purpose: Serialize/deserialize bill items

Serialization (For storage):
    items_list = [(sku, name, qty, price), ...]
    
    serialized = ""
    FOR EACH item in items_list:
        serialized += f"{sku}:{name}:{qty}:{price};"
    
    Result: "P001:Notebook:2:50.0;P002:Pen:3:15.0;"
    
Deserialization (For display):
    serialized = "P001:Notebook:2:50.0;P002:Pen:3:15.0;"
    
    items = []
    FOR EACH item_string in serialized.split(";"):
        sku, name, qty, price = item_string.split(":")
        items.append((sku, name, qty, price))
```

---

## Data Processing Flows

### Flow 1: Add Product Process

```
User Input
    ├─ SKU (string)
    ├─ Name (string)
    ├─ Price (float)
    └─ Stock (int)
        ↓
Validation
    ├─ SKU must be unique
    └─ Fields must not be empty
        ↓
Database Insert
    └─ INSERT INTO products
        ↓
Commit
    ├─ Transaction committed
    └─ Database persisted
        ↓
User Feedback
    └─ "✓ Added {name}"
```

### Flow 2: Billing Process

```
Item Collection
    ├─ Read SKU
    ├─ Validate exists
    ├─ Read Quantity
    └─ Validate amount
        ↓
Stock Deduction
    ├─ Check available
    └─ Update database
        ↓
Total Calculation
    ├─ qty × price for each
    └─ Sum all items
        ↓
Database Storage
    ├─ Save bill record
    └─ Save items list
        ↓
PDF Generation
    ├─ Create document
    ├─ Format content
    └─ Save to disk
        ↓
Completion
    └─ Display success
```

---

## State Machines

### Application State Machine

```
        ┌─────────────────────┐
        │   Application Start │
        └──────────┬──────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │ Initialize Database  │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │  Display Main Menu   │
        └──────────┬───────────┘
                   │
        ┌──────────┴─────────────────┐
        │                            │
        ▼                            ▼
    ┌────────┐               ┌────────────┐
    │ Choice │ ─────────────→ │ Execute    │
    │ 0-6    │               │ Function   │
    └────────┘               └──────┬─────┘
        ▲                           │
        │                           ▼
        │                    ┌────────────┐
        │                    │ Update UI  │
        │                    │ (Display)  │
        │                    └──────┬─────┘
        │                           │
        └───────────────────────────┘
                   (0 = Exit)
                   │
                   ▼
        ┌──────────────────────┐
        │  Display Goodbye     │
        └──────────┬───────────┘
                   │
                   ▼
        ┌──────────────────────┐
        │   Application End    │
        └──────────────────────┘
```

---

**End of Pseudo Code Documentation**


