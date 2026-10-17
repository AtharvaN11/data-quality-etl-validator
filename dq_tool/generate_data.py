"""Step 1: Generate fake (synthetic) data with Faker, then deliberately break some of it.

Why break it? A validation tool needs bad data to catch. We inject known defects
(duplicates, nulls, bad emails, text in number columns, orphan foreign keys, ...)
so we can prove each check really works.
"""
import random

import pandas as pd
from faker import Faker

SEED = 42  # fixed seed => same data every run => repeatable results


def generate_customers(n=500, seed=SEED):
    """Create n clean customer rows."""
    fake = Faker()
    Faker.seed(seed)
    random.seed(seed)
    rows = []
    for customer_id in range(1, n + 1):
        rows.append(
            {
                "customer_id": customer_id,
                "name": fake.name(),
                "email": fake.email(),
                "age": random.randint(18, 80),
                "signup_date": fake.date_between("-3y", "today").isoformat(),
                "country": fake.country(),
            }
        )
    df = pd.DataFrame(rows)
    df["age"] = df["age"].astype(object)  # object lets us put text like "unknown" in later
    return df


def generate_orders(customer_ids, n=1500, seed=SEED):
    """Create n clean order rows that each point at a real customer."""
    fake = Faker()
    Faker.seed(seed)
    rng = random.Random(seed)
    rows = []
    for order_id in range(1, n + 1):
        rows.append(
            {
                "order_id": order_id,
                "customer_id": rng.choice(list(customer_ids)),
                "amount": round(rng.uniform(5, 500), 2),
                "order_date": fake.date_between("-1y", "today").isoformat(),
                "status": rng.choice(["PLACED", "SHIPPED", "DELIVERED", "CANCELLED"]),
            }
        )
    return pd.DataFrame(rows)


def inject_customer_defects(df, seed=SEED):
    """Break the clean customers table in known ways."""
    rng = random.Random(seed)
    df = df.copy()
    idx = list(df.index)
    rng.shuffle(idx)

    df.loc[idx[0:15], "email"] = None  # 15 missing emails
    for i in idx[15:27]:  # 12 emails without '@'
        df.loc[i, "email"] = df.loc[i, "email"].replace("@", "")
    df.loc[idx[27:35], "age"] = "unknown"  # 8 text values in a numeric column
    df.loc[idx[35:38], "age"] = 150  # 3 impossible ages
    df.loc[idx[38:41], "age"] = -5  # 3 negative ages
    df.loc[idx[41:46], "name"] = None  # 5 missing names

    dupes = df.sample(10, random_state=seed)  # 10 exact duplicate rows
    return pd.concat([df, dupes], ignore_index=True)


def inject_order_defects(df, seed=SEED):
    """Break the clean orders table in known ways."""
    rng = random.Random(seed)
    df = df.copy()
    idx = list(df.index)
    rng.shuffle(idx)

    df.loc[idx[0:20], "customer_id"] = [9000 + i for i in range(20)]  # 20 orphan orders
    df.loc[idx[20:30], "amount"] = -1 * df.loc[idx[20:30], "amount"]  # 10 negative amounts
    df.loc[idx[30:40], "order_date"] = None  # 10 missing dates

    dupes = df.sample(5, random_state=seed)  # 5 duplicate rows
    return pd.concat([df, dupes], ignore_index=True)


def generate_all(n_customers=500, n_orders=1500):
    """Return (customers, orders) DataFrames containing injected defects."""
    customers = generate_customers(n_customers)
    orders = generate_orders(customers["customer_id"], n_orders)
    return inject_customer_defects(customers), inject_order_defects(orders)
