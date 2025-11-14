---

# 📦 E-commerce Synthetic Data Pipeline

This project demonstrates a complete mini data pipeline built in **Python** using **Faker**, **Pandas**, and **SQLite**.
The goal is to generate realistic e-commerce data, store it in a relational database, and query it using SQL joins.

---

## 🚀 Project Overview

The project consists of **three main parts**:

### **1. Synthetic Data Generation**

Using `faker` and `pandas`, I generated **5 realistic e-commerce CSV files**:

| File Name         | Description                                        |
| ----------------- | -------------------------------------------------- |
| `customers.csv`   | Customer details (name, email, city, signup_date)  |
| `products.csv`    | List of products with category and price           |
| `orders.csv`      | Orders linked to customers                         |
| `order_items.csv` | Line items for each order (product, qty, subtotal) |
| `payments.csv`    | Payment details per order                          |

Each file contains **500–1000 records** with clean, realistic fields.

---

### **2. Ingesting CSVs into SQLite**

Python was used (via **sqlite3 / SQLAlchemy**) to:

* Create a SQLite database named **`ecommerce.db`**
* Create all required tables
* Load the 5 CSVs
* Insert the data into the database

This creates a complete local relational data model for analytics.

---

### **3. SQL Query — Multi-table Join**

An SQL query was written to join:

* `customers`
* `orders`
* `order_items`
* `products`

The result returns a detailed order breakdown:

* Customer name
* Order ID
* Order date
* Product name
* Quantity ordered
* Subtotal per item
* Total amount per order

This mimics a real-world e-commerce analytics dashboard query.

---

## 🛠️ Technologies Used

* **Python**
* **Pandas**
* **Faker**
* **SQLite / sqlite3**
* **SQL joins**

---

## 📁 How to Run the Project

### **1. Install Dependencies**

```bash
pip install pandas faker
```

### **2. Generate CSV Files**

```bash
python data_generation.py
```

### **3. Create and Populate SQLite Database**

```bash
python data_ingest.py
```

### **4. Run SQL Join Query**

You can run the SQL query using Python or sqlite3:

```bash
sqlite3 ecommerce.db < queries.sql
```

Or inside Python:

```bash
import sqlite3, pandas as pd

conn = sqlite3.connect("ecommerce.db")
df = pd.read_sql_query("""
SELECT 
    c.name AS customer_name,
    o.order_id,
    o.order_date,
    p.name AS product_name,
    oi.quantity,
    oi.subtotal,
    o.total_amount
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
ORDER BY o.order_date DESC
LIMIT 20;
""", conn)

print(df)
```

---

## 📌 Summary

✔️ Generated synthetic e-commerce datasets
✔️ Stored them in SQLite using Python
✔️ Ran SQL joins to produce analytical insights



---



