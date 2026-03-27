from __future__ import annotations

from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, File, HTTPException, UploadFile, status

import backend.routes.query as query_module
from backend.services.data_service import process_uploaded_csv

router = APIRouter()

RAW_DATA_DIR = Path("data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_CONTENT_TYPES = {
    "text/csv",
    "application/vnd.ms-excel",
    "application/csv",
    "text/plain",
}

MAX_FILE_SIZE_BYTES = 25 * 1024 * 1024


@router.post("/upload")
async def upload_csv(file: UploadFile = File(...)) -> dict:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No filename provided.",
        )

    suffix = Path(file.filename).suffix.lower()
    if suffix != ".csv":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only CSV files are supported right now.",
        )

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported content type: {file.content_type}",
        )

    contents = await file.read()
    if not contents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    if len(contents) > MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds the 25 MB limit for this MVP.",
        )

    saved_name = f"{uuid4().hex}_{Path(file.filename).name}"
    saved_path = RAW_DATA_DIR / saved_name

    try:
        saved_path.write_bytes(contents)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to save file: {exc}",
        ) from exc

    try:
        result = process_uploaded_csv(saved_path)

        if "cleaned_df" not in result:
            raise ValueError("Processing result missing 'cleaned_df'")

        query_module.GLOBAL_DF = result["cleaned_df"]

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process file: {exc}",
        ) from exc

    return {
        "message": "File uploaded and processed successfully.",
        "original_filename": file.filename,
        "saved_path": str(saved_path),
        "result": {
            "status": "success",
            "original_shape": result["original_shape"],
            "cleaned_shape": result["cleaned_shape"],
            "cleaning_report": result["cleaning_report"],
            "schema_before": result["schema_before"],
            "schema_after": result["schema_after"],
            "insights": result["insights"],
            "preview": result["preview"],
            "summary": result["summary"],
            "llm_analysis": result["llm_analysis"],
            "sql_queries": result["sql_queries"],
        },
    }