"""Step 4: Run every rule and write the summary report.

Usage:
    python -m dq_tool.run_validation
"""
import sqlite3
from pathlib import Path

import pandas as pd

from dq_tool import checks
from dq_tool.load_data import DEFAULT_DB, build_database

REPORT_DIR = Path("reports")


def load_tables(db_path):
    """Read all four tables from the database into DataFrames."""
    with sqlite3.connect(db_path) as conn:
        return {
            name: pd.read_sql(f"SELECT * FROM {name}", conn)
            for name in ("src_customers", "src_orders", "tgt_customers", "tgt_orders")
        }


def run_all_checks(t):
    """Apply every validation rule and return a list of result dicts."""
    results = [
        # ---- Source customers ----
        checks.check_duplicates(t["src_customers"], "src_customers", "customer_id"),
        checks.check_nulls(t["src_customers"], "src_customers", "email"),
        checks.check_nulls(t["src_customers"], "src_customers", "name"),
        checks.check_email_format(t["src_customers"], "src_customers", "email"),
        checks.check_numeric_type(t["src_customers"], "src_customers", "age"),
        checks.check_range(t["src_customers"], "src_customers", "age", 18, 100),
        # ---- Source orders ----
        checks.check_duplicates(t["src_orders"], "src_orders", "order_id"),
        checks.check_nulls(t["src_orders"], "src_orders", "order_date"),
        checks.check_range(t["src_orders"], "src_orders", "amount", low=0.01),
        checks.check_referential_integrity(
            t["src_orders"], t["src_customers"], "src_orders", "customer_id", "customer_id"
        ),
        # ---- Source -> Target reconciliation ----
        checks.check_row_count(t["src_customers"], t["tgt_customers"], "customers"),
        checks.check_row_count(t["src_orders"], t["tgt_orders"], "orders"),
        checks.check_missing_keys(t["src_customers"], t["tgt_customers"], "customers", "customer_id"),
        checks.check_missing_keys(t["src_orders"], t["tgt_orders"], "orders", "order_id"),
        # ---- Target tables should be cleaner after ETL ----
        checks.check_duplicates(t["tgt_customers"], "tgt_customers", "customer_id"),
        checks.check_nulls(t["tgt_customers"], "tgt_customers", "email"),
        checks.check_duplicates(t["tgt_orders"], "tgt_orders", "order_id"),
        checks.check_nulls(t["tgt_orders"], "tgt_orders", "order_date"),
    ]
    return results


def write_reports(results, total_records, out_dir=REPORT_DIR):
    """Save the results as CSV (for Excel) and Markdown (for humans)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame(results)
    df.to_csv(out_dir / "validation_report.csv", index=False)

    failed = df[df["status"] == "FAIL"]
    lines = [
        "# Data Quality Validation Report",
        "",
        f"- **Rules executed:** {len(df)}",
        f"- **Records scanned (source + target):** {total_records:,}",
        f"- **Passed:** {len(df) - len(failed)}  |  **Failed:** {len(failed)}",
        "",
        "## Failed checks by table and rule",
        "",
        "| Table | Rule | Column | Failed rows | Total rows |",
        "|---|---|---|---:|---:|",
    ]
    for _, r in failed.sort_values(["table", "rule"]).iterrows():
        lines.append(f"| {r['table']} | {r['rule']} | {r['column']} | {r['failed']} | {r['total']} |")

    lines += ["", "## All checks", "", "| Status | Table | Rule | Column | Failed | Total |", "|---|---|---|---|---:|---:|"]
    for _, r in df.iterrows():
        icon = "PASS" if r["status"] == "PASS" else "FAIL"
        lines.append(f"| {icon} | {r['table']} | {r['rule']} | {r['column']} | {r['failed']} | {r['total']} |")

    (out_dir / "validation_report.md").write_text("\n".join(lines) + "\n")
    return df


def main():
    db_path = build_database(DEFAULT_DB)
    tables = load_tables(db_path)
    total_records = sum(len(df) for df in tables.values())
    df = write_reports(run_all_checks(tables), total_records)

    print(df.to_string(index=False))
    print(f"\n{len(df)} rules run on {total_records:,} records "
          f"-> {(df['status'] == 'FAIL').sum()} failed.")
    print(f"Reports saved in {REPORT_DIR}/")


if __name__ == "__main__":
    main()
