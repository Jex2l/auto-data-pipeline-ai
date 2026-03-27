import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def generate_query_code(df, question):
    columns = ", ".join(df.columns)

    prompt = f"""
    You are a Python data analyst.

    You are given a pandas dataframe named `df`.

    Column names are:
    {list(df.columns)}

    IMPORTANT RULES:
    - Only use EXISTING column names exactly as given
    - Do NOT guess column names
    - Do NOT explain anything
    - Do NOT use markdown
    - ONLY output executable Python code
    - Store final result in variable `result`

    Allowed operations:
    - df["col"].min()
    - df["col"].max()
    - df["col"].mean()
    - df.sort_values()
    - df.head()

    Question:
    {question}
    """

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )
    code = response.json().get("response", "").strip()

    if not code:
        code = "result = df.head()"
    return response.json()["response"]