"""Step 3: The validation rules.

Every check takes one or more DataFrames and returns ONE result (a dict):
    rule, table, column, failed, total, status ("PASS" / "FAIL")

Keeping every check small and independent makes them easy to test and to read.
"""
import re

import pandas as pd

EMAIL_PATTERN = re.compile(r"^[\w.+-]+@[\w-]+\.[\w.-]+$")


def _result(rule, table, column, failed, total):
    return {
        "rule": rule,
        "table": table,
        "column": column,
        "failed": int(failed),
        "total": int(total),
        "status": "PASS" if failed == 0 else "FAIL",
    }


def check_duplicates(df, table, column):
    """Rule: the key column must be unique (no repeated IDs)."""
    failed = df.duplicated(subset=[column], keep="first").sum()
    return _result("Duplicate check", table, column, failed, len(df))


def check_nulls(df, table, column):
    """Rule: the column must not contain empty (NULL) values."""
    return _result("Null check", table, column, df[column].isna().sum(), len(df))


def check_email_format(df, table, column):
    """Rule: non-empty emails must look like name@domain.com."""
    values = df[column].dropna().astype(str)
    failed = (~values.str.match(EMAIL_PATTERN)).sum()
    return _result("Email format check", table, column, failed, len(df))


def check_numeric_type(df, table, column):
    """Rule: the column must hold numbers only (no text like 'unknown')."""
    present = df[column].dropna()
    converted = pd.to_numeric(present, errors="coerce")
    return _result("Data type check", table, column, converted.isna().sum(), len(df))


def check_range(df, table, column, low=None, high=None):
    """Rule: numeric values must stay inside [low, high]."""
    values = pd.to_numeric(df[column], errors="coerce").dropna()
    bad = pd.Series(False, index=values.index)
    if low is not None:
        bad |= values < low
    if high is not None:
        bad |= values > high
    return _result("Range check", table, column, bad.sum(), len(df))


def check_referential_integrity(child, parent, table, child_col, parent_col):
    """Rule: every child key must exist in the parent table (no orphans)."""
    orphans = ~child[child_col].isin(parent[parent_col])
    return _result("Referential integrity", table, child_col, orphans.sum(), len(child))


def check_row_count(source, target, table):
    """Rule: source and target should have the same number of rows."""
    failed = abs(len(source) - len(target))
    return _result("Row count match", table, "(all rows)", failed, len(source))


def check_missing_keys(source, target, table, key):
    """Rule: every distinct source key must still exist in the target."""
    source_keys = set(source[key].dropna())
    missing = source_keys - set(target[key].dropna())
    return _result("Source-to-target key match", table, key, len(missing), len(source_keys))
