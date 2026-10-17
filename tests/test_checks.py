"""Unit tests: each check is tested on a tiny DataFrame where we KNOW the answer."""
import pandas as pd

from dq_tool import checks


def test_duplicates_detected():
    df = pd.DataFrame({"id": [1, 2, 2, 3, 3, 3]})
    result = checks.check_duplicates(df, "t", "id")
    assert result["failed"] == 3
    assert result["status"] == "FAIL"


def test_duplicates_pass_when_unique():
    df = pd.DataFrame({"id": [1, 2, 3]})
    assert checks.check_duplicates(df, "t", "id")["status"] == "PASS"


def test_nulls_detected():
    df = pd.DataFrame({"email": ["a@x.com", None, None]})
    assert checks.check_nulls(df, "t", "email")["failed"] == 2


def test_email_format():
    df = pd.DataFrame({"email": ["good@site.com", "bad-email.com", None]})
    result = checks.check_email_format(df, "t", "email")
    assert result["failed"] == 1  # None is a null problem, not a format problem


def test_numeric_type_catches_text():
    df = pd.DataFrame({"age": [25, "unknown", 40, "abc"]})
    assert checks.check_numeric_type(df, "t", "age")["failed"] == 2


def test_range_check():
    df = pd.DataFrame({"age": [10, 25, 150, -5, 60]})
    assert checks.check_range(df, "t", "age", low=18, high=100)["failed"] == 3


def test_referential_integrity_finds_orphans():
    parent = pd.DataFrame({"customer_id": [1, 2, 3]})
    child = pd.DataFrame({"customer_id": [1, 2, 99, 100]})
    result = checks.check_referential_integrity(child, parent, "orders", "customer_id", "customer_id")
    assert result["failed"] == 2


def test_row_count_mismatch():
    src = pd.DataFrame({"id": range(10)})
    tgt = pd.DataFrame({"id": range(7)})
    assert checks.check_row_count(src, tgt, "t")["failed"] == 3


def test_missing_keys_between_source_and_target():
    src = pd.DataFrame({"id": [1, 2, 3, 4]})
    tgt = pd.DataFrame({"id": [1, 2]})
    assert checks.check_missing_keys(src, tgt, "t", "id")["failed"] == 2
