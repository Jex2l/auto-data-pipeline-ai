import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3"


def analyze_dataset(df):
    sample = df.head(10).to_string()

    prompt = f"""
You are a senior data analyst.

Analyze this dataset sample:

{sample}

Provide:
1. What this dataset represents
2. Key patterns
3. Data quality issues
4. Recommended next steps
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
        return "LLM failed to respond."

    return response.json().get("response", "No response from LLM")