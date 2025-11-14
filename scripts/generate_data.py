#!/usr/bin/env python3
"""Generate synthetic e-commerce datasets with realistic relationships."""
from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import List

from faker import Faker

faker = Faker("en_IN")
Faker.seed(2024)
random.seed(2024)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
MIN_ROWS = 500
MAX_ROWS = 1500

PRODUCT_CATEGORIES = [
    "Electronics",
    "Fashion",
    "Home & Kitchen",
    "Beauty",
    "Sports",
    "Books",
    "Grocery",
    "Toys",
]
ORDER_STATUSES = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
PAYMENT_MODES = ["UPI", "Credit Card", "Debit Card", "Net Banking", "Wallet", "COD"]


@dataclass
class Product:
    product_id: str
    name: str
    category: str
    price: Decimal


@dataclass
class Customer:
    customer_id: str
    name: str
    email: str
    country: str


@dataclass
class Order:
    order_id: str
    customer_id: str
    order_date: date
    status: str


@dataclass
class OrderItem:
    item_id: str
    order_id: str
    product_id: str
    quantity: int


@dataclass
class Payment:
    payment_id: str
    order_id: str
    amount: Decimal
    mode: str
    payment_date: date


def ensure_data_dir() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def random_row_count() -> int:
    return random.randint(MIN_ROWS, MAX_ROWS)


def generate_customers(count: int) -> List[Customer]:
    customers: List[Customer] = []
    faker.unique.clear()
    for idx in range(1, count + 1):
        customer_id = f"CUST{idx:05d}"
        name = faker.name()
        email = faker.unique.email()
        customers.append(Customer(customer_id, name, email, "India"))
    return customers


def generate_products(count: int) -> List[Product]:
    adjectives = ["Premium", "Classic", "Eco", "Smart", "Urban", "Elite", "Daily"]
    nouns = [
        "Phone",
        "Shoes",
        "Mixer",
        "Lamp",
        "Watch",
        "Backpack",
        "Bottle",
        "Headphones",
        "Saree",
        "Kurta",
    ]
    products: List[Product] = []
    for idx in range(1, count + 1):
        product_id = f"PROD{idx:05d}"
        name = f"{random.choice(adjectives)} {random.choice(nouns)}"
        category = random.choice(PRODUCT_CATEGORIES)
        price_paise = random.randint(19_900, 199_9900)
        price = (Decimal(price_paise) / Decimal("100")).quantize(Decimal("0.01"))
        products.append(Product(product_id, name, category, price))
    return products


def generate_orders(count: int, customers: List[Customer]) -> List[Order]:
    orders: List[Order] = []
    for idx in range(1, count + 1):
        order_id = f"ORD{idx:06d}"
        customer = random.choice(customers)
        order_date = faker.date_between(start_date="-365d", end_date="today")
        status = random.choice(ORDER_STATUSES)
        orders.append(Order(order_id, customer.customer_id, order_date, status))
    return orders


def distribute_order_items(
    target_count: int,
    orders: List[Order],
    products: List[Product],
) -> tuple[List[OrderItem], dict[str, Decimal]]:
    order_items: List[OrderItem] = []
    order_totals: dict[str, Decimal] = {order.order_id: Decimal("0.00") for order in orders}
    product_price_map = {product.product_id: product.price for product in products}

    if target_count < len(orders):
        target_count = len(orders)

    for idx, order in enumerate(orders):
        orders_remaining = len(orders) - (idx + 1)
        items_left = target_count - len(order_items)
        max_for_order = items_left - orders_remaining
        if orders_remaining == 0:
            items_for_order = max_for_order
        else:
            soft_cap = 5
            items_for_order = random.randint(1, max(1, min(soft_cap, max_for_order)))

        for _ in range(items_for_order):
            item_id = f"ITEM{len(order_items) + 1:06d}"
            product = random.choice(products)
            quantity = random.randint(1, 5)
            order_items.append(OrderItem(item_id, order.order_id, product.product_id, quantity))
            line_total = product_price_map[product.product_id] * Decimal(quantity)
            order_totals[order.order_id] += line_total

    return order_items, order_totals


def generate_payments(orders: List[Order], order_totals: dict[str, Decimal]) -> List[Payment]:
    payments: List[Payment] = []
    for idx, order in enumerate(orders, start=1):
        amount = order_totals[order.order_id].quantize(Decimal("0.01"))
        payment_date = order.order_date + timedelta(days=random.randint(0, 3))
        mode = random.choice(PAYMENT_MODES)
        payments.append(
            Payment(
                payment_id=f"PAY{idx:06d}",
                order_id=order.order_id,
                amount=amount,
                mode=mode,
                payment_date=payment_date,
            )
        )
    return payments


def write_csv(filename: str, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    file_path = DATA_DIR / filename
    with file_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    ensure_data_dir()

    customer_count = random_row_count()
    product_count = random_row_count()
    order_count = random_row_count()
    order_items_target = random_row_count()

    customers = generate_customers(customer_count)
    products = generate_products(product_count)
    orders = generate_orders(order_count, customers)
    order_items, order_totals = distribute_order_items(order_items_target, orders, products)
    payments = generate_payments(orders, order_totals)

    write_csv(
        "customers.csv",
        ["customer_id", "name", "email", "country"],
        [customer.__dict__ for customer in customers],
    )

    write_csv(
        "products.csv",
        ["product_id", "name", "category", "price"],
        [
            {
                "product_id": product.product_id,
                "name": product.name,
                "category": product.category,
                "price": format(product.price, ".2f"),
            }
            for product in products
        ],
    )

    write_csv(
        "orders.csv",
        ["order_id", "customer_id", "order_date", "status"],
        [
            {
                "order_id": order.order_id,
                "customer_id": order.customer_id,
                "order_date": order.order_date.isoformat(),
                "status": order.status,
            }
            for order in orders
        ],
    )

    write_csv(
        "order_items.csv",
        ["item_id", "order_id", "product_id", "quantity"],
        [item.__dict__ for item in order_items],
    )

    write_csv(
        "payments.csv",
        ["payment_id", "order_id", "amount", "mode", "payment_date"],
        [
            {
                "payment_id": payment.payment_id,
                "order_id": payment.order_id,
                "amount": format(payment.amount, ".2f"),
                "mode": payment.mode,
                "payment_date": payment.payment_date.isoformat(),
            }
            for payment in payments
        ],
    )

    print("Synthetic datasets generated in", DATA_DIR)


if __name__ == "__main__":
    main()
