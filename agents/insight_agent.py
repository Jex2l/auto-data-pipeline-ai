from __future__ import annotations

import pandas as pd


def generate_basic_insights(df: pd.DataFrame) -> dict:
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=["number"]).columns.tolist()

    insights = {
        "row_count": int(df.shape[0]),
        "column_count": int(df.shape[1]),
        "numeric_columns": numeric_cols,
        "categorical_columns": categorical_cols,
        "numeric_summary": {},
        "top_categories": {},
    }

    for col in numeric_cols[:10]:
        series = df[col].dropna()
        if not series.empty:
            insights["numeric_summary"][col] = {
                "min": float(series.min()),
                "max": float(series.max()),
                "mean": float(series.mean()),
                "median": float(series.median()),
            }

    for col in categorical_cols[:10]:
        series = df[col].dropna().astype(str)
        if not series.empty:
            insights["top_categories"][col] = (
                series.value_counts().head(5).to_dict()
            )

    return insights