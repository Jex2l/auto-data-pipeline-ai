from __future__ import annotations

import pandas as pd


def infer_schema_summary(df: pd.DataFrame) -> dict:
    columns = []
    for col in df.columns:
        series = df[col]
        columns.append(
            {
                "name": str(col),
                "dtype": str(series.dtype),
                "non_null_count": int(series.notna().sum()),
                "null_count": int(series.isna().sum()),
                "unique_count": int(series.nunique(dropna=True)),
                "sample_values": [
                    None if pd.isna(v) else str(v)
                    for v in series.dropna().astype(str).head(3).tolist()
                ],
            }
        )

    return {
        "column_count": int(len(df.columns)),
        "row_count": int(len(df)),
        "columns": columns,
    }