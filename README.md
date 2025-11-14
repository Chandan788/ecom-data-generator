E-Commerce Data Generator & Reporting System
This project automatically generates realistic synthetic e-commerce datasets, loads them into SQLite, and produces a clean reporting output.

📦 Features
✔ Data Generator (scripts/generate_data.py)
Creates 5 interconnected CSV files:

customers.csv

products.csv

orders.csv

order_items.csv

payments.csv

Ensures:

Valid customer → orders

Valid order → items

Valid item → product

Valid payments = total order amount

Generates realistic Indian-style data using Faker

✔ SQLite Ingestion (scripts/ingest_to_sqlite.py)
Builds SQLite database at:
db/ecom.db

Creates tables with:

Primary keys

Foreign keys

Loads CSVs

Validates row counts

Prints success logs

✔ SQL Reporting (scripts/report.sql)
Generates a final report containing:

customer_name

order_id

order_date

product_name

category

quantity

price

total_item_amount

payment_mode

Filters:

Only successful payments

Sorted by order_date DESC

✔ Report Runner (scripts/run_report.py)
Loads SQL from report.sql

Runs against SQLite

Prints pretty table to terminal

Saves CSV to /data/final_report.csv

📁 Project Structure
ecom-data-generator/
│
├── data/
│   ├── customers.csv
│   ├── products.csv
│   ├── orders.csv
│   ├── order_items.csv
│   └── payments.csv
│
├── db/
│   └── ecom.db
│
├── scripts/
│   ├── generate_data.py
│   ├── ingest_to_sqlite.py
│   ├── run_report.py
│   └── report.sql
│
├── requirements.txt
└── README.md
🚀 How to Run the Project
1. Install dependencies
pip install -r requirements.txt
2. Generate synthetic data
python scripts/generate_data.py
3. Ingest data into SQLite
python scripts/ingest_to_sqlite.py
4. Run report
python scripts/run_report.py
Outputs:

Pretty table in terminal

/data/final_report.csv

🧰 Tech Stack
Python

Faker

Pandas

SQLite (sqlite3)

Tabulate

📌 Author
Chandan Kumar B
(GitHub: @Chandan788)
