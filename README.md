# Data Quality & ETL Validation Tool

An automated tool that **generates synthetic data, loads it into a SQL database, runs an ETL step, and then validates the result** with 18 data quality rules. It produces a summary report of every failed check by table and rule.

**Tech:** Python · Pandas · SQL (SQLite) · Faker · Pytest

## What it does

```
Faker  ──►  raw data with        ──►  SQL database  ──►  ETL (SQL)  ──►  Validation  ──►  Report
(fake data) deliberate defects        (src_ tables)      (tgt_ tables)    (18 rules)      (CSV + Markdown)
```

1. **Generate** – Faker creates 500 customers and 1,500 orders, then deliberately injects known defects.
2. **Load** – the raw data is loaded into SQLite as *source* tables (`src_customers`, `src_orders`).
3. **ETL** – a SQL script keeps valid, unique rows in *target* tables (`tgt_customers`, `tgt_orders`) and moves every rejected row, with a `rejection_reason`, into `quarantine_customers` / `quarantine_orders`.
4. **Validate** – Pandas checks run on the source, target and quarantine tables.
5. **Report** – failed checks are summarised by table and rule in `reports/`.

## Validation rules

| Category | Rule | Example |
|---|---|---|
| Duplicates | Key column must be unique | repeated `customer_id` |
| Nulls | Required columns must be filled | missing `email` |
| Format | Emails must look like `name@domain.com` | `john.example.com` |
| Data type | Numeric columns must hold numbers | age = `"unknown"` |
| Range | Values must be realistic | age = 150, amount = -20 |
| Referential integrity | Every order must belong to a real customer | orphan `customer_id` |
| Source-to-target | source = target + quarantine (rows and keys) | rows lost in ETL |

## Results

Running `python -m dq_tool.run_validation` scans **3,807 records** (source + target) with **18 rules**: **10 fail on purpose** and **8 pass**.

| Table | Rows in | Clean (target) | Quarantined |
|---|---:|---:|---:|
| customers | 510 | 454 | 56 |
| orders | 1,505 | 1,338 | 167 |

**The 10 failures are the injected defects, caught with exact counts** (source tables):

| Table | Rule | Column | Failed rows |
|---|---|---|---:|
| src_customers | Duplicate check | customer_id | 10 |
| src_customers | Null check | email | 15 |
| src_customers | Null check | name | 5 |
| src_customers | Email format check | email | 12 |
| src_customers | Data type check | age | 8 |
| src_customers | Range check | age | 7 |
| src_orders | Duplicate check | order_id | 5 |
| src_orders | Null check | order_date | 10 |
| src_orders | Range check | amount | 10 |
| src_orders | Referential integrity | customer_id | 20 |

**The 8 passes prove the ETL works:**

- `tgt_customers` and `tgt_orders` have no duplicate keys and no nulls in `email` / `order_date`.
- Row count and key match pass for both tables: every source row is either loaded or quarantined (510 = 454 + 56 and 1,505 = 1,338 + 167), so nothing is silently lost.

**Why rows were quarantined**

| Table | Reason | Rows |
|---|---|---:|
| quarantine_customers | duplicate_customer_id | 10 |
| | missing_email | 15 |
| | invalid_email | 12 |
| | missing_name | 5 |
| | invalid_age_type | 8 |
| | age_out_of_range | 6 |
| quarantine_orders | duplicate_order_id | 5 |
| | missing_order_date | 10 |
| | invalid_amount | 10 |
| | orphan_customer_id | 20 |
| | rejected_customer | 122 |

`rejected_customer` means the order itself was valid, but its customer was quarantined, so it cannot be loaded without breaking referential integrity.

All 14 automated tests (13 unit tests and 1 end-to-end test) pass.

## Run it

```bash
pip install -r requirements.txt

python -m dq_tool.run_validation   # builds the database, runs all checks, writes reports/
python -m pytest -v                # runs the automated tests
```

Output: `reports/validation_report.md` and `reports/validation_report.csv`.

## Project structure

```
dq_tool/
  generate_data.py    Faker data + injected defects
  load_data.py        loads SQLite tables, runs the ETL SQL
  checks.py           the validation rules (one small function each)
  run_validation.py   runs every rule, writes the report
tests/
  test_checks.py      unit tests for each rule on tiny known data
  test_pipeline.py    end-to-end test: counts, reconciliation, quarantine reasons
data/warehouse.db     generated SQLite database (src_, tgt_, quarantine_ tables)
reports/              generated validation_report.csv and .md
STUDY_GUIDE.md        glossary, code walkthrough, interview Q&A
```

## Design notes

- **Seeded randomness** – results are identical on every run, so tests can assert exact counts.
- **One function per rule** – each check is small, independent and unit-tested.
- **SQLite for portability** – no database install needed. The SQL is standard and ports to MySQL / SQL Server with minor syntax changes.
