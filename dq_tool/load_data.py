"""Step 2: Load the raw data into a database, then run a small ETL step.

We use SQLite because it needs no installation (it is built into Python).
All SQL used here also works on MySQL / SQL Server with small syntax tweaks.

Tables created:
  src_customers, src_orders  -> the raw "source" data (still dirty)
  tgt_customers, tgt_orders  -> the "target" data after our ETL clean-up step
"""
import sqlite3
from pathlib import Path

from dq_tool.generate_data import generate_all

DEFAULT_DB = Path("data/warehouse.db")

# The ETL step written in plain SQL. It removes exact duplicate rows and
# drops rows that are missing a required field (email / order_date).
ETL_SQL = """
DROP TABLE IF EXISTS tgt_customers;
CREATE TABLE tgt_customers AS
SELECT DISTINCT customer_id, name, email, age, signup_date, country
FROM src_customers
WHERE email IS NOT NULL;

DROP TABLE IF EXISTS tgt_orders;
CREATE TABLE tgt_orders AS
SELECT DISTINCT order_id, customer_id, amount, order_date, status
FROM src_orders
WHERE order_date IS NOT NULL;
"""


def build_database(db_path=DEFAULT_DB, n_customers=500, n_orders=1500):
    """Generate fake data, load it as source tables, run ETL, return the db path."""
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    customers, orders = generate_all(n_customers, n_orders)

    with sqlite3.connect(db_path) as conn:
        customers.to_sql("src_customers", conn, if_exists="replace", index=False)
        orders.to_sql("src_orders", conn, if_exists="replace", index=False)
        conn.executescript(ETL_SQL)
    return db_path


if __name__ == "__main__":
    path = build_database()
    print(f"Database created at {path}")
