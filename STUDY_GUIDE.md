# Study Guide (read this before any interview)

## 1. Glossary - plain-English terms

| Term | Meaning |
|---|---|
| **ETL** | Extract (read data from a source), Transform (clean/reshape it), Load (write it to a destination). Here: raw tables -> clean tables. |
| **Source / Target** | Source = where data comes from. Target = where it ends up after ETL. |
| **Data quality** | How correct, complete and consistent data is. |
| **Validation** | Automatically checking data against rules. |
| **Synthetic data** | Fake but realistic data, made with **Faker**, so you never touch real customer info. |
| **Null** | A missing/empty value. |
| **Duplicate** | The same record appearing more than once. |
| **Primary key** | A column that uniquely identifies each row (e.g. `customer_id`). |
| **Foreign key** | A column that points to another table's key (`orders.customer_id` -> `customers.customer_id`). |
| **Referential integrity** | Every foreign key must match a real row in the parent table. A violation is an **orphan record**. |
| **Reconciliation** | Comparing source and target after ETL to confirm nothing was lost or changed wrongly. |
| **DataFrame** | A Pandas table in memory (rows and columns). |
| **Regex** | A text pattern, used here to check email format. |
| **Unit test** | A small test of one function. **Pytest** is the tool that runs them. |
| **Assertion** | A line in a test saying "this must be true" (`assert x == 3`). |
| **Seed** | A fixed starting number that makes random data repeatable. |
| **SQLite** | A tiny SQL database stored in one file; built into Python. |

## 2. How the code flows (read files in this order)

1. `generate_data.py` - builds clean fake data, then `inject_*_defects` breaks it in known ways (15 null emails, 12 bad emails, 8 text ages, 20 orphan orders, duplicates...). Because we know how many defects exist, tests can prove the checks find exactly that many.
2. `load_data.py` - `to_sql` writes DataFrames into SQLite tables. `ETL_SQL` is real SQL: `SELECT DISTINCT` removes duplicates, `WHERE ... IS NOT NULL` drops incomplete rows.
3. `checks.py` - each function receives a DataFrame, counts failures, and returns a result: rule, table, column, failed, total, PASS/FAIL.
4. `run_validation.py` - reads the tables, calls every check, builds the report.
5. `tests/` - `test_checks.py` feeds tiny tables with known answers; `test_pipeline.py` runs everything end to end.

## 3. Key code ideas to understand

- `df.duplicated(subset=["id"])` marks repeated keys; `.sum()` counts them.
- `df["col"].isna()` finds nulls.
- `pd.to_numeric(x, errors="coerce")` turns text like "unknown" into NaN - that is how the data type check works.
- `child["customer_id"].isin(parent["customer_id"])` is the whole referential integrity check; `~` flips it to find orphans.
- Source-to-target: compare `len(source)` vs `len(target)` and compare sets of keys.

## 4. Interview questions with answers

**Q: What does your project do?**
It generates fake data with defects, loads it into a SQL database, runs an ETL step, then validates source and target with 18 rules and reports failures by table and rule.

**Q: Why synthetic data?**
It is safe (no real personal data), repeatable (seeded), and I control the defects, so I can prove each check works.

**Q: How do you detect duplicates / orphans?**
Duplicates with `df.duplicated` on the key column. Orphans by checking whether each order's `customer_id` exists in the customers table (`isin`); in SQL that is a `LEFT JOIN ... WHERE parent.id IS NULL`.

**Q: What is source-to-target validation?**
After ETL, compare the target against the source: row counts and keys. If keys exist in source but not target, rows were lost.

**Q: Why do the source-to-target row counts fail?**
By design. My ETL removes duplicates and incomplete rows, so counts differ. The report shows exactly how many rows were removed, and the target-table checks confirm duplicates and nulls are gone. In real projects you would compare against *expected* removals.

**Q: Why Pytest?**
Unit tests prove each rule works on known data, and the end-to-end test guards against breaking the pipeline when I change code.

**Q: Why SQLite and not MySQL / SQL Server?**
No setup required, so anyone can run the project. The SQL is standard; moving to MySQL means swapping the connection (e.g. SQLAlchemy) and a few syntax differences such as `AUTO_INCREMENT`.

**Q: How would you improve it?**
Load rules from a config file, add checks for value consistency between tables, add scheduling and email alerts, and support MySQL via SQLAlchemy.

## 5. One-hour study plan

1. 10 min - read the glossary until you can explain each term aloud.
2. 15 min - run `python -m dq_tool.run_validation`; open `reports/validation_report.md` and match each failed row to a defect in `generate_data.py`.
3. 15 min - read `checks.py`; for each function, say what it counts.
4. 10 min - run `python -m pytest -v`; read one test and see why it passes.
5. 10 min - practise the interview answers above.
