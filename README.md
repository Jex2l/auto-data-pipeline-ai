# auto-data-pipeline-ai

Upload a CSV, get it profiled, cleaned, and summarized — with natural
language querying on top, powered by a local LLM (Ollama).

## What it actually does

```
Streamlit UI  ──POST /api/upload (CSV)──►  FastAPI backend
                                               │
                                   pandas: schema profile (before/after),
                                   dedup + normalize, basic numeric/
                                   categorical stats
                                               │
                              cleaned CSV + JSON report → data/processed/
```

```
Streamlit UI  ──POST /api/ask (question)──►  FastAPI backend
                                               │
                              asks local Ollama (llama3) to write pandas
                              code answering the question, runs it
                              against the uploaded dataframe via exec()
```

- **Backend**: FastAPI (`backend/main.py`), routes in `backend/routes/`.
- **Frontend**: a single-file Streamlit app (`frontend/app.py`).
- **Agents** (`agents/`): plain Python functions, not an agent framework —
  schema profiling, cleaning, insight stats, and two LLM-backed agents
  (`llm_agent.py`, `sql_agent.py`, `query_agent.py`) that all call a
  **local Ollama server** directly over HTTP, not LangChain or OpenAI.
- **Tests** (`tests/`): real but narrow — unit tests for schema inference
  and cleaning logic only. Nothing covers the upload/query routes or the
  Ollama-dependent agents.

`pipelines/`, `infra/`, `docs/`, and `notebooks/` are currently **empty
directories** — placeholders for future work, not implemented yet.

## Setup

You need **Ollama running locally** with a model pulled — the `/api/ask`
natural-language query feature (and the `llm_agent`/`sql_agent` paths)
depend on it and degrade to error strings if it's unreachable.

```bash
# 1. Ollama
brew install ollama        # or see ollama.com for your platform
ollama serve &
ollama pull llama3

# 2. Python deps
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 3. Backend (separate terminal)
uvicorn backend.main:app --reload --port 8000

# 4. Frontend (separate terminal)
streamlit run frontend/app.py
```

Three separate manual steps (plus Ollama) — there's no `docker-compose.yml`
or root script wiring them together yet.

## Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /api/upload` | Upload a CSV; returns the cleaned data + schema/insight report |
| `POST /api/ask` | Ask a natural-language question about the uploaded data |

## Known limitations

- **No sandboxing on `/api/ask`**: the LLM-generated pandas code runs via
  plain `exec()` against the uploaded dataframe, with no sandboxing beyond
  a prompt instruction not to do anything unsafe. Treat this as
  arbitrary-code-execution-by-design — fine for local/trusted use, not
  something to expose publicly as-is.
- Despite the directory names, `agents/` isn't an agent framework and
  `pipelines/`/`infra/` are empty — this is a working two-service upload →
  clean → insight → ask app, not yet the fuller platform the folder
  structure implies.
- `agents/pipeline_agent.py` and `agents/utils.py` aren't imported or used
  anywhere in the current code — likely the start of the unimplemented
  "pipeline plan" feature. Left in place but unwired; worth either
  finishing or removing.
- Only CSV upload is implemented, despite earlier docs mentioning JSON —
  there's no JSON upload path in `backend/routes/upload.py`.
- No Spark — despite the project name and earlier docs, all processing is
  plain pandas.

## Fixed in this pass

- `agents/query_agent.py` had a bug where `generate_query_code()` computed
  a `code` variable (with a sane fallback if the LLM returned nothing) and
  then discarded it, re-parsing the raw HTTP response and returning that
  instead — silently bypassing the fallback. Now returns `code` as intended.
- `requirements.txt` listed `langchain` and `openai`, neither of which is
  imported anywhere (all LLM calls go to a local Ollama server via plain
  `requests`), while actually missing `requests` and `matplotlib` (both
  used in `backend/services/query_services.py` and the `agents/` modules).
  Replaced the unused entries with the real ones.
