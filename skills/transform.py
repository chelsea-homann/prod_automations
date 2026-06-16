"""
Skills 2.1-2.5 - Data transformation & cleaning
===============================================
Small, composable DataFrame transforms. Every function returns a new/modified
frame and tolerates missing columns so a schema drift never crashes a run.

Usage
-----
    from skills import transform as tx

    df = tx.standardize_columns(df, RENAMES)
    df = tx.keep_columns(df, ["A", "B"])
    df = tx.format_dates(df, contains=("Date",))
    df = tx.add_stamp(df, "Launch Date")
"""

import pandas as pd


def standardize_columns(df, renames):
    """Skill 2.1 - rename columns using ``renames``, ignoring absent keys."""
    existing = {k: v for k, v in renames.items() if k in df.columns}
    return df.rename(columns=existing)


def keep_columns(df, columns_to_keep):
    """
    Skill 2.2 - keep only ``columns_to_keep`` that are present, preserving order.
    If ``columns_to_keep`` is falsy, the frame is returned unchanged.
    """
    if not columns_to_keep:
        return df
    available = [c for c in columns_to_keep if c in df.columns]
    print(f"Filtered to {len(available)} columns")
    return df[available].copy()


def format_dates(df, contains=("Date",), fmt="%m/%d/%Y"):
    """
    Skill 2.3 - reformat date-like columns whose name contains any token in
    ``contains``. Unparseable columns are left untouched.
    """
    df = df.copy()
    for col in df.columns:
        if any(token in col for token in contains):
            try:
                df[col] = pd.to_datetime(df[col]).dt.strftime(fmt)
            except Exception:  # noqa: BLE001 - non-date column, skip silently
                pass
    return df


def add_stamp(df, column, value=None, fmt="%m-%d-%Y", drop=None):
    """
    Skill 2.4 - add a derived/audit column (defaults to today's date) and
    optionally drop a superseded source column.
    """
    from datetime import date
    df = df.copy()
    df[column] = value if value is not None else date.today().strftime(fmt)
    if drop and drop in df.columns:
        df = df.drop(columns=[drop])
    return df


def parse_skip_rows(skip_rows_str):
    """
    Skill 2.5 - turn a "0,2" style env value into a list of int indices, or None.
    Pair with ``pd.read_csv(f, header=0, skiprows=lambda x: x in skip_rows)``.
    """
    if not skip_rows_str:
        return None
    return [int(x) for x in skip_rows_str.split(",") if x.strip()]
