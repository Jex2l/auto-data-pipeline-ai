from fastapi import APIRouter
from pydantic import BaseModel

from agents.query_agent import generate_query_code
from backend.services.query_services import execute_query

router = APIRouter()

# Global storage (MVP only)
GLOBAL_DF = None


class QueryRequest(BaseModel):
    question: str


@router.post("/ask")
def ask_question(req: QueryRequest):
    global GLOBAL_DF

    if GLOBAL_DF is None:
        return {
            "success": False,
            "error": "No dataset loaded",
            "generated_code": None,
            "result": None,
            "image": None
        }

    try:
        code = generate_query_code(GLOBAL_DF, req.question)
        result, image = execute_query(GLOBAL_DF, code)

        return {
            "success": True,
            "generated_code": code,
            "result": str(result),
            "image": image,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "generated_code": None,
            "result": None,
            "image": None
        }