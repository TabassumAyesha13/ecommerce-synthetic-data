import sqlite3

import pandas as pd


QUERY = """
SELECT
  c.customer_id,
  c.first_name || ' ' || c.last_name AS customer_name,
  o.order_id,
  o.order_date,
  p.name AS product_name,
  oi.quantity,
  ROUND(oi.line_total, 2) AS line_subtotal,
  ROUND(o.order_total, 2) AS order_total
FROM customers c
JOIN orders o
  ON o.customer_id = c.customer_id
JOIN order_items oi
  ON oi.order_id = o.order_id
JOIN products p
  ON p.product_id = oi.product_id
ORDER BY o.order_id, oi.order_item_id
LIMIT 20;
"""


def main():
    conn = sqlite3.connect("ecommerce.db")
    df = pd.read_sql_query(QUERY, conn)
    print(df.to_string(index=False))
    conn.close()


if __name__ == "__main__":
    main()


