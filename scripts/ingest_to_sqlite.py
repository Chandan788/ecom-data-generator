#!/usr/bin/env python3
"""Load generated CSV datasets into a SQLite database."""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Dict, Tuple

import pandas as pd

ROOT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT_DIR / "data"
DB_DIR = ROOT_DIR / "db"
DB_PATH = DB_DIR / "ecom.db"

CSV_TABLES: Dict[str, Tuple[str, str]] = {
    "customers.csv": (
        "customers",
        """
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            country TEXT NOT NULL
        );
        """,
    ),
    "products.csv": (
        "products",
        """
        CREATE TABLE IF NOT EXISTS products (
            product_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL
        );
        """,
    ),
    "orders.csv": (
        "orders",
        """
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            order_date TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
        );
        """,
    ),
    "order_items.csv": (
        "order_items",
        """
        CREATE TABLE IF NOT EXISTS order_items (
            item_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            product_id TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            FOREIGN KEY (order_id) REFERENCES orders(order_id),
            FOREIGN KEY (product_id) REFERENCES products(product_id)
        );
        """,
    ),
    "payments.csv": (
        "payments",
        """
        CREATE TABLE IF NOT EXISTS payments (
            payment_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            amount REAL NOT NULL,
            mode TEXT NOT NULL,
            payment_date TEXT NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        );
        """,
    ),
}

TABLE_ORDER = [
    "customers.csv",
    "products.csv",
    "orders.csv",
    "order_items.csv",
    "payments.csv",
]


def ensure_dirs() -> None:
    DB_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def init_db() -> sqlite3.Connection:
    ensure_dirs()
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    drop_statements = [f"DROP TABLE IF EXISTS {table_name};" for _, (table_name, _) in CSV_TABLES.items()]
    schema_statements = [schema for _, (_, schema) in CSV_TABLES.items()]
    conn.executescript("\n".join(drop_statements + schema_statements))
    return conn


def normalize_dataframe(table: str, df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if table == "customers":
        df["name"] = df["name"].astype(str)
    elif table == "products":
        df["price"] = df["price"].astype(float)
    elif table == "orders":
        df["order_date"] = pd.to_datetime(df["order_date"]).dt.strftime("%Y-%m-%d")
    elif table == "order_items":
        df["quantity"] = df["quantity"].astype(int)
    elif table == "payments":
        df["amount"] = df["amount"].astype(float)
        df["payment_date"] = pd.to_datetime(df["payment_date"]).dt.strftime("%Y-%m-%d")
    return df


def ingest_table(conn: sqlite3.Connection, csv_filename: str) -> int:
    table_name, _ = CSV_TABLES[csv_filename]
    csv_path = DATA_DIR / csv_filename
    if not csv_path.exists():
        raise FileNotFoundError(f"Missing required CSV file: {csv_path}")

    df = pd.read_csv(csv_path)
    df = normalize_dataframe(table_name, df)
    expected_rows = len(df)
    df.to_sql(table_name, conn, if_exists="append", index=False)

    result = conn.execute(f"SELECT COUNT(*) FROM {table_name};").fetchone()
    if result is None:
        raise RuntimeError(f"Unable to fetch row count for table {table_name}")
    count_in_db = result[0]
    if count_in_db != expected_rows:
        raise ValueError(
            f"Row count mismatch for {table_name}: expected {expected_rows}, got {count_in_db}"
        )
    print(f"Loaded {count_in_db} rows into '{table_name}' successfully.")
    return count_in_db


def main() -> None:
    with init_db() as conn:
        total_rows = 0
        for csv_filename in TABLE_ORDER:
            total_rows += ingest_table(conn, csv_filename)
        conn.commit()
    print(f"All tables loaded into SQLite database at {DB_PATH} (total rows: {total_rows}).")


if __name__ == "__main__":
    main()
