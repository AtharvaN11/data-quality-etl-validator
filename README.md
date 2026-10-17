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
3. **ETL** – a SQL script removes duplicates and rows missing required fields, writing *target* tables (`tgt_customers`, `tgt_orders`).
4. **Validate** – Pandas + SQL checks run on source and target tables.
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
| Source-to-target | Row counts and keys must reconcile after ETL | rows lost in ETL |

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
  test_checks.py      unit test for each rule on tiny known data
  test_pipeline.py    end-to-end test of the full pipeline
STUDY_GUIDE.md        glossary, code walkthrough, interview Q&A
```

## Design notes

- **Seeded randomness** – results are identical on every run, so tests can assert exact counts.
- **One function per rule** – each check is small, independent and unit-tested.
- **SQLite for portability** – no database install needed. The SQL is standard and ports to MySQL / SQL Server with minor syntax changes.
