from __future__ import annotations

import re
from typing import Tuple

import pandas as pd


def _normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    renamed = []
    seen = set()

    for col in df.columns:
        clean = re.sub(r"\s+", "_", str(col).strip().lower())
        clean = re.sub(r"[^a-zA-Z0-9_]", "", clean)
        if not clean:
            clean = "column"

        base = clean
        counter = 1
        while clean in seen:
            clean = f"{base}_{counter}"
            counter += 1

        seen.add(clean)
        renamed.append(clean)

    df.columns = renamed
    return df


def _strip_string_cells(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.select_dtypes(include=["object", "string"]).columns:
        df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def _replace_common_null_tokens(df: pd.DataFrame) -> pd.DataFrame:
    null_tokens = {"", "na", "n/a", "null", "none", "nan", "missing", "-"}
    for col in df.columns:
        if df[col].dtype == "object" or str(df[col].dtype).startswith("string"):
            df[col] = df[col].apply(
                lambda x: pd.NA
                if isinstance(x, str) and x.strip().lower() in null_tokens
                else x
            )
    return df


def _try_numeric_conversion(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        if df[col].dtype == "object" or str(df[col].dtype).startswith("string"):
            converted = pd.to_numeric(df[col], errors="ignore")
            df[col] = converted
    return df


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    working = df.copy(deep=True)

    original_rows = int(working.shape[0])
    original_cols = int(working.shape[1])
    original_nulls = int(working.isna().sum().sum())
    duplicate_rows_before = int(working.duplicated().sum())

    working = _normalize_column_names(working)
    working = _strip_string_cells(working)
    working = _replace_common_null_tokens(working)
    working = _try_numeric_conversion(working)

    working = working.drop_duplicates().reset_index(drop=True)

    # Drop completely empty rows and columns
    working = working.dropna(how="all")
    working = working.dropna(axis=1, how="all")

    final_nulls = int(working.isna().sum().sum())

    report = {
        "original_rows": original_rows,
        "original_columns": original_cols,
        "cleaned_rows": int(working.shape[0]),
        "cleaned_columns": int(working.shape[1]),
        "duplicates_removed": duplicate_rows_before,
        "null_cells_before": original_nulls,
        "null_cells_after": final_nulls,
        "columns_after_cleaning": list(map(str, working.columns.tolist())),
    }

    return working, report