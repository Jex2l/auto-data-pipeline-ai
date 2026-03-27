import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_query_code(df, user_query):
    columns = ", ".join(df.columns)

    prompt = f"""
You are a Python data analyst.

Dataset columns:
{columns}

User question:
{user_query}

Write Python pandas code to answer this.

Rules:
- Use dataframe name: df
- Only return code
- If visualization is needed, use matplotlib

Example:
result = df['salary'].mean()
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]