#!/usr/bin/env python3
"""Execute the SQL report and present results."""
from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
from tabulate import tabulate

ROOT_DIR = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_DIR / "db" / "ecom.db"
REPORT_SQL_PATH = ROOT_DIR / "scripts" / "report.sql"
OUTPUT_CSV_PATH = ROOT_DIR / "data" / "final_report.csv"


def load_sql() -> str:
    if not REPORT_SQL_PATH.exists():
        raise FileNotFoundError(f"Missing SQL file: {REPORT_SQL_PATH}")
    return REPORT_SQL_PATH.read_text(encoding="utf-8")


def run_report(sql: str) -> pd.DataFrame:
    if not DB_PATH.exists():
        raise FileNotFoundError("SQLite database not found. Run ingestion first.")
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)


def display_table(df: pd.DataFrame) -> None:
    if df.empty:
        print("No rows returned by the report.")
    else:
        print(tabulate(df, headers="keys", tablefmt="psql", showindex=False))


def save_csv(df: pd.DataFrame) -> None:
    OUTPUT_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV_PATH, index=False)
    print(f"Report saved to {OUTPUT_CSV_PATH}")


def main() -> None:
    sql = load_sql()
    df = run_report(sql)
    display_table(df)
    if not df.empty:
        save_csv(df)


if __name__ == "__main__":
    main()
