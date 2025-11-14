import random
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


def random_date(start_days_ago: int = 730, end_days_ago: int = 0) -> datetime:
    """Return a random datetime between today - start_days_ago and today - end_days_ago."""
    if start_days_ago < end_days_ago:
        raise ValueError("start_days_ago must be >= end_days_ago")
    days_offset = random.randint(end_days_ago, start_days_ago)
    random_seconds = random.randint(0, 86400)
    return datetime.now() - timedelta(days=days_offset, seconds=random_seconds)


def generate_customers(fake: Faker, count: int) -> pd.DataFrame:
    customers = []
    for customer_id in range(1, count + 1):
        profile = fake.simple_profile()
        address = fake.address().split("\n")
        street = address[0]
        city_state_zip = address[1].split()
        city = fake.city()
        state = city_state_zip[-2] if len(city_state_zip) >= 2 else fake.state_abbr()
        postal_code = city_state_zip[-1] if len(city_state_zip) >= 1 else fake.postcode()

        customers.append(
            {
                "customer_id": customer_id,
                "first_name": profile["name"].split()[0],
                "last_name": profile["name"].split()[-1],
                "email": profile["mail"],
                "phone": fake.phone_number(),
                "street_address": street,
                "city": city,
                "state": state,
                "postal_code": postal_code,
                "country": "USA",
                "signup_date": fake.date_between(start_date="-5y", end_date="today"),
                "loyalty_score": round(random.uniform(0, 100), 2),
            }
        )
    return pd.DataFrame(customers)


def generate_products(fake: Faker, count: int) -> pd.DataFrame:
    categories = [
        "Electronics",
        "Home & Kitchen",
        "Apparel",
        "Health & Beauty",
        "Sports & Outdoors",
        "Books",
        "Toys & Games",
    ]
    brands = [fake.company() for _ in range(20)]

    products = []
    for product_id in range(1, count + 1):
        category = random.choice(categories)
        base_price = round(random.uniform(5, 500), 2)
        cost = round(base_price * random.uniform(0.4, 0.8), 2)
        products.append(
            {
                "product_id": product_id,
                "name": fake.catch_phrase(),
                "category": category,
                "brand": random.choice(brands),
                "sku": f"SKU-{product_id:05d}",
                "price": base_price,
                "cost": cost,
                "stock_quantity": random.randint(0, 1000),
                "created_at": fake.date_between(start_date="-3y", end_date="today"),
            }
        )
    return pd.DataFrame(products)


def generate_orders(fake: Faker, customer_ids, count: int) -> pd.DataFrame:
    statuses = ["Pending", "Processing", "Completed", "Cancelled", "Returned"]
    shipping_methods = ["Ground", "2-Day", "Overnight", "Pickup"]
    orders = []
    for order_id in range(1, count + 1):
        order_date = random_date()
        status = random.choices(
            population=statuses, weights=[0.1, 0.25, 0.5, 0.1, 0.05], k=1
        )[0]

        orders.append(
            {
                "order_id": order_id,
                "customer_id": random.choice(customer_ids),
                "order_date": order_date,
                "status": status,
                "shipping_method": random.choice(shipping_methods),
                "shipping_cost": round(random.uniform(0, 25), 2),
                "order_subtotal": 0.0,
                "order_total": 0.0,
                "currency": "USD",
                "payment_status": "Pending",
            }
        )
    return pd.DataFrame(orders)


def generate_order_items(order_df: pd.DataFrame, product_df: pd.DataFrame, target_count: int):
    order_items = []
    order_totals = {order_id: 0.0 for order_id in order_df["order_id"]}
    order_subtotals = {order_id: 0.0 for order_id in order_df["order_id"]}

    products = product_df.to_dict("records")
    order_ids = order_df["order_id"].tolist()

    order_item_id = 1
    for order_id in order_ids:
        num_items = random.randint(1, 4)
        for _ in range(num_items):
            if order_item_id > target_count:
                break
            product = random.choice(products)
            quantity = random.randint(1, 5)
            unit_price = product["price"] * random.uniform(0.9, 1.1)
            discount_rate = random.choice([0, 0.05, 0.1, 0.15])
            discount = round(discount_rate * unit_price, 2)
            line_total = round((unit_price - discount) * quantity, 2)

            order_items.append(
                {
                    "order_item_id": order_item_id,
                    "order_id": order_id,
                    "product_id": product["product_id"],
                    "quantity": quantity,
                    "unit_price": round(unit_price, 2),
                    "discount": discount,
                    "line_total": line_total,
                }
            )
            order_subtotals[order_id] += line_total
            order_totals[order_id] = order_subtotals[order_id]
            order_item_id += 1
        if order_item_id > target_count:
            break

    order_items_df = pd.DataFrame(order_items)
    return order_items_df, order_subtotals


def attach_totals(order_df: pd.DataFrame, order_subtotals: dict) -> pd.DataFrame:
    updated_orders = order_df.copy()
    for idx, row in updated_orders.iterrows():
        subtotal = round(order_subtotals.get(row["order_id"], 0.0), 2)
        total = round(subtotal + row["shipping_cost"], 2)
        updated_orders.at[idx, "order_subtotal"] = subtotal
        updated_orders.at[idx, "order_total"] = total
        updated_orders.at[idx, "payment_status"] = (
            "Paid" if total > 0 and random.random() > 0.1 else "Pending"
        )
    return updated_orders


def generate_payments(order_df: pd.DataFrame) -> pd.DataFrame:
    methods = ["Credit Card", "Debit Card", "PayPal", "Gift Card", "Bank Transfer"]
    payment_statuses = ["Completed", "Pending", "Failed", "Refunded"]

    payments = []
    for order in order_df.to_dict("records"):
        payment_status = random.choices(
            population=payment_statuses,
            weights=[0.75, 0.1, 0.1, 0.05],
            k=1,
        )[0]
        if payment_status == "Completed":
            amount = order["order_total"]
        elif payment_status == "Refunded":
            amount = round(order["order_total"] * -1, 2)
        elif payment_status == "Pending":
            amount = round(order["order_total"] * 0.5, 2)
        else:
            amount = 0.0

        payments.append(
            {
                "payment_id": len(payments) + 1,
                "order_id": order["order_id"],
                "customer_id": order["customer_id"],
                "payment_date": order["order_date"] + timedelta(
                    days=random.randint(0, 5)
                ),
                "payment_method": random.choice(methods),
                "payment_amount": round(amount, 2),
                "transaction_id": f"TXN-{random.randint(10_000_000, 99_999_999)}",
                "status": payment_status,
            }
        )
    return pd.DataFrame(payments)


def main():
    random.seed(42)
    fake = Faker()
    Faker.seed(42)

    output_dir = Path(".")

    num_customers = 800
    num_products = 600
    num_orders = 900
    num_order_items = 950

    customers_df = generate_customers(fake, num_customers)
    products_df = generate_products(fake, num_products)
    orders_df = generate_orders(fake, customers_df["customer_id"].tolist(), num_orders)
    order_items_df, order_subtotals = generate_order_items(orders_df, products_df, num_order_items)
    orders_df = attach_totals(orders_df, order_subtotals)
    payments_df = generate_payments(orders_df)

    customers_df.to_csv(output_dir / "customers.csv", index=False)
    products_df.to_csv(output_dir / "products.csv", index=False)
    orders_df.to_csv(output_dir / "orders.csv", index=False)
    order_items_df.to_csv(output_dir / "order_items.csv", index=False)
    payments_df.to_csv(output_dir / "payments.csv", index=False)

    summary = {
        "customers.csv": len(customers_df),
        "products.csv": len(products_df),
        "orders.csv": len(orders_df),
        "order_items.csv": len(order_items_df),
        "payments.csv": len(payments_df),
    }

    print("Synthetic e-commerce dataset generated successfully.")
    for filename, count in summary.items():
        print(f" - {filename}: {count} rows")


if __name__ == "__main__":
    main()


