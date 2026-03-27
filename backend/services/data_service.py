from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from agents.cleaning_agent import clean_dataframe
from agents.insight_agent import generate_basic_insights
from agents.schema_agent import infer_schema_summary

PROCESSED_DIR = Path("data/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def process_uploaded_csv(csv_path: Path) -> dict:
    if not csv_path.exists():
        raise ValueError("CSV file does not exist.")

    try:
        df = pd.read_csv(csv_path)
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(csv_path, encoding="latin-1")
        except Exception as exc:
            raise ValueError(f"Could not decode CSV file: {exc}") from exc
    except pd.errors.EmptyDataError as exc:
        raise ValueError("CSV has no rows.") from exc
    except Exception as exc:
        raise ValueError(f"Could not read CSV: {exc}") from exc

    if df.empty:
        raise ValueError("CSV is valid but contains no data rows.")

    original_shape = {"rows": int(df.shape[0]), "columns": int(df.shape[1])}
    schema_before = infer_schema_summary(df)

    cleaned_df, cleaning_report = clean_dataframe(df)
    schema_after = infer_schema_summary(cleaned_df)
    insights = generate_basic_insights(cleaned_df)

    output_csv = PROCESSED_DIR / f"{csv_path.stem}_cleaned.csv"
    output_json = PROCESSED_DIR / f"{csv_path.stem}_report.json"

    cleaned_df.to_csv(output_csv, index=False)

    report_payload = {
        "original_shape": original_shape,
        "cleaned_shape": {
            "rows": int(cleaned_df.shape[0]),
            "columns": int(cleaned_df.shape[1]),
        },
        "schema_before": schema_before,
        "schema_after": schema_after,
        "cleaning_report": cleaning_report,
        "insights": insights,
    }

    output_json.write_text(json.dumps(report_payload, indent=2, default=str))

    preview_records = cleaned_df.head(20).to_dict(orient="records")

    return {
        "original_shape": original_shape,
        "cleaned_shape": {
            "rows": int(cleaned_df.shape[0]),
            "columns": int(cleaned_df.shape[1]),
        },
        "schema_before": schema_before,
        "schema_after": schema_after,
        "cleaning_report": cleaning_report,
        "insights": insights,
        "preview": preview_records,
        "processed_csv_path": str(output_csv),
        "report_json_path": str(output_json),
    }