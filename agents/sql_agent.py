import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_sql(df):
    columns = ", ".join(df.columns)

    prompt = f"""
You are a SQL expert.

Dataset columns:
{columns}

Generate 3 useful SQL queries for analysis.

Only return SQL queries.
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    if response.status_code != 200:
        return "SQL generation failed."

    return response.json().get("response", "No SQL generated")