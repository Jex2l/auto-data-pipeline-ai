from fastapi import APIRouter
from pydantic import BaseModel
import pandas as pd

from agents.query_agent import generate_query_code
from backend.services.query_services import execute_query

router = APIRouter()

# TEMP: store dataframe globally (later improve)
GLOBAL_DF = None


class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(req: QueryRequest):
    global GLOBAL_DF

    if GLOBAL_DF is None:
        return {"error": "No dataset loaded"}

    code = generate_query_code(GLOBAL_DF, req.question)
    result, image = execute_query(GLOBAL_DF, code)

    return {
        "generated_code": code,
        "result": str(result),
        "image": image
    }