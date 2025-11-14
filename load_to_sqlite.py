import sqlite3
from pathlib import Path

import pandas as pd


def load_csv_to_sqlite(csv_path: Path, table_name: str, connection: sqlite3.Connection):
    """Load a CSV file into a SQLite table, replacing existing data."""
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, connection, if_exists="replace", index=False)
    print(f"Imported {len(df):>4} rows into '{table_name}'.")


def main():
    base_dir = Path(".")
    db_path = base_dir / "ecommerce.db"

    csv_tables = {
        "customers": base_dir / "customers.csv",
        "products": base_dir / "products.csv",
        "orders": base_dir / "orders.csv",
        "order_items": base_dir / "order_items.csv",
        "payments": base_dir / "payments.csv",
    }

    missing = [name for name, path in csv_tables.items() if not path.exists()]
    if missing:
        raise FileNotFoundError(f"Missing CSV files: {', '.join(missing)}")

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = OFF;")
        for table, csv_path in csv_tables.items():
            load_csv_to_sqlite(csv_path, table, conn)
        conn.commit()

    print(f"Data successfully loaded into {db_path.resolve()}")


if __name__ == "__main__":
    main()


