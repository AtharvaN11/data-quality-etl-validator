# Data Quality Validation Report

- **Rules executed:** 18
- **Records scanned (source + target):** 3,990
- **Passed:** 4  |  **Failed:** 14

## Failed checks by table and rule

| Table | Rule | Column | Failed rows | Total rows |
|---|---|---|---:|---:|
| customers | Row count match | (all rows) | 25 | 510 |
| customers | Source-to-target key match | customer_id | 15 | 500 |
| orders | Row count match | (all rows) | 15 | 1505 |
| orders | Source-to-target key match | order_id | 10 | 1500 |
| src_customers | Data type check | age | 8 | 510 |
| src_customers | Duplicate check | customer_id | 10 | 510 |
| src_customers | Email format check | email | 12 | 510 |
| src_customers | Null check | email | 15 | 510 |
| src_customers | Null check | name | 5 | 510 |
| src_customers | Range check | age | 7 | 510 |
| src_orders | Duplicate check | order_id | 5 | 1505 |
| src_orders | Null check | order_date | 10 | 1505 |
| src_orders | Range check | amount | 10 | 1505 |
| src_orders | Referential integrity | customer_id | 20 | 1505 |

## All checks

| Status | Table | Rule | Column | Failed | Total |
|---|---|---|---|---:|---:|
| FAIL | src_customers | Duplicate check | customer_id | 10 | 510 |
| FAIL | src_customers | Null check | email | 15 | 510 |
| FAIL | src_customers | Null check | name | 5 | 510 |
| FAIL | src_customers | Email format check | email | 12 | 510 |
| FAIL | src_customers | Data type check | age | 8 | 510 |
| FAIL | src_customers | Range check | age | 7 | 510 |
| FAIL | src_orders | Duplicate check | order_id | 5 | 1505 |
| FAIL | src_orders | Null check | order_date | 10 | 1505 |
| FAIL | src_orders | Range check | amount | 10 | 1505 |
| FAIL | src_orders | Referential integrity | customer_id | 20 | 1505 |
| FAIL | customers | Row count match | (all rows) | 25 | 510 |
| FAIL | orders | Row count match | (all rows) | 15 | 1505 |
| FAIL | customers | Source-to-target key match | customer_id | 15 | 500 |
| FAIL | orders | Source-to-target key match | order_id | 10 | 1500 |
| PASS | tgt_customers | Duplicate check | customer_id | 0 | 485 |
| PASS | tgt_customers | Null check | email | 0 | 485 |
| PASS | tgt_orders | Duplicate check | order_id | 0 | 1490 |
| PASS | tgt_orders | Null check | order_date | 0 | 1490 |
