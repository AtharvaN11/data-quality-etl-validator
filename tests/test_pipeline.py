"""End-to-end test: generate data -> load DB -> run ETL -> run all checks -> write reports."""
from dq_tool.load_data import build_database
from dq_tool.run_validation import load_tables, run_all_checks, write_reports


def test_full_pipeline(tmp_path):
    db = build_database(tmp_path / "test.db")
    tables = load_tables(db)
    results = run_all_checks(tables)
    df = write_reports(results, sum(len(t) for t in tables.values()), tmp_path)

    by_key = {(r["table"], r["rule"], r["column"]): r for r in results}

    # The defects we injected must be caught with the exact counts.
    assert by_key[("src_customers", "Duplicate check", "customer_id")]["failed"] == 10
    assert by_key[("src_customers", "Null check", "email")]["failed"] == 15
    assert by_key[("src_customers", "Email format check", "email")]["failed"] == 12
    assert by_key[("src_customers", "Data type check", "age")]["failed"] == 8
    assert by_key[("src_orders", "Referential integrity", "customer_id")]["failed"] == 20

    # After ETL, duplicates and nulls must be gone from the target tables.
    assert by_key[("tgt_customers", "Duplicate check", "customer_id")]["status"] == "PASS"
    assert by_key[("tgt_orders", "Null check", "order_date")]["status"] == "PASS"

    assert (tmp_path / "validation_report.csv").exists()
    assert (tmp_path / "validation_report.md").exists()
    assert len(df) == len(results)
