# 🚀 Auto Data Pipeline AI

An AI-powered data engineering assistant that automates data ingestion, cleaning, analysis, visualization, and querying — all through a simple UI.

---

## 📌 Overview

Auto Data Pipeline AI is a full-stack application that allows users to:

* Upload raw CSV datasets
* Automatically clean and preprocess data
* Generate schema summaries and insights
* Ask natural language questions about the dataset, with an optional chart back
* Get answers powered by a local LLM + Python execution

This project bridges the gap between **data engineering, analytics, and AI**, enabling non-technical users to interact with data like a data scientist.

---

## 🧠 Key Features

### 📂 Data Ingestion

* Upload CSV files through the Streamlit UI (CSV only, 25MB max)
* File-type validation
* Automatic storage under `data/raw/`

### 🧹 Data Cleaning

* Deduplication and missing-value handling
* Column name normalization
* Cleaning report generation

### 📊 Data Insights

* Schema inference before and after cleaning
* Basic numeric/categorical statistical insights

### 🤖 AI Query Engine

* Ask questions in natural language
* A local LLM (Ollama) converts the question → Pandas code
* Executes the generated code against the uploaded dataframe
* Returns a result, plus a chart image if the generated code produced one (matplotlib)

---

## 🏗️ Architecture

```
Streamlit UI  ──POST /api/upload (CSV)──►  FastAPI backend
                                               │
                                   pandas: schema profile (before/after),
                                   dedup + normalize, basic numeric/
                                   categorical stats
                                               │
                              cleaned CSV + JSON report → data/processed/

Streamlit UI  ──POST /api/ask (question)──►  FastAPI backend
                                               │
                              asks a local Ollama server to write pandas
                              code answering the question, runs it
                              against the uploaded dataframe via exec()
```

---

## 🛠️ Tech Stack

### 🔹 Frontend
* Streamlit — a single-file app (`frontend/app.py`)

### 🔹 Backend
* FastAPI + Uvicorn

### 🔹 Data Processing
* Pandas, NumPy

### 🔹 AI / LLM
* **Local Ollama (llama3)**, called directly over HTTP via `requests` — not
  LangChain or a hosted API. `/api/ask` degrades to an error string if
  Ollama isn't running.

### 🔹 Visualization
* Matplotlib — the LLM-generated code can produce a chart, which is
  returned to the UI as a base64 PNG alongside the result

---

## 📂 Project Structure

```
auto-data-pipeline-ai/
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── upload.py
│   │   └── query.py
│   └── services/
│       ├── data_service.py
│       └── query_services.py
├── agents/
│   ├── cleaning_agent.py
│   ├── query_agent.py
│   ├── insight_agent.py
│   ├── schema_agent.py
│   ├── llm_agent.py
│   ├── sql_agent.py
│   ├── pipeline_agent.py   # not wired up yet, see Known limitations
│   └── utils.py            # not wired up yet, see Known limitations
├── frontend/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── pipelines/   # currently empty - placeholder
├── infra/       # currently empty - placeholder
├── docs/        # currently empty - placeholder
├── notebooks/   # currently empty - placeholder
├── tests/
│   ├── test_schema.py
│   └── test_cleaning.py
└── README.md
```

`agents/` is a set of plain Python functions, not an agent framework, and
`pipelines/`/`infra/`/`docs/`/`notebooks/` are empty — placeholders for
future work rather than implemented features. Tests cover schema inference
and cleaning logic only; the upload/query routes and the Ollama-dependent
agents aren't covered.

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the repository

```bash
git clone https://github.com/Jex2l/auto-data-pipeline-ai.git
cd auto-data-pipeline-ai
```

### 2️⃣ Install and start Ollama

The `/api/ask` feature needs a local Ollama server with a model pulled:

```bash
brew install ollama        # or see ollama.com for your platform
ollama serve &
ollama pull llama3
```

### 3️⃣ Create a virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows

pip install -r requirements.txt
```

### 4️⃣ Run the backend

```bash
uvicorn backend.main:app --reload
```

Runs at `http://127.0.0.1:8000`.

### 5️⃣ Run the frontend (separate terminal)

```bash
streamlit run frontend/app.py
```

There's no `docker-compose.yml` or root script wiring these three pieces
(Ollama, backend, frontend) together yet — each is started manually.

---

## 📊 How It Works

1. **Upload** — user uploads a CSV; the backend saves and processes it.
2. **Clean & profile** — dedup, type/column normalization, before/after
   schema and basic stats, written to `data/processed/`.
3. **Ask** — user asks a natural-language question; the local LLM generates
   Pandas code, the backend executes it, and returns the result (plus a
   chart if the code produced one).

### 🧪 Example queries

**✅ Supported**
* What is the average volume?
* What is the minimum close value?
* Show top 5 highest values
* What is the total volume?

**❌ Not recommended (LLM limitation)**
* Longest increasing streak
* Complex time-series patterns
* Multi-step logical reasoning

---

## 🔒 Error handling

* Non-CSV uploads and files over 25MB are rejected
* Generated code runs inside a `try`/`except` that reports the error back
  instead of crashing the request
* `/api/ask` falls back to a plain error string if Ollama is unreachable

⚠️ **Not a sandbox**: the LLM-generated code runs via plain `exec()` against
the uploaded dataframe, with no sandboxing beyond a prompt instruction not
to do anything unsafe. Fine for local/trusted use; don't expose this
publicly as-is.

---

## Known limitations

* `agents/pipeline_agent.py` and `agents/utils.py` aren't imported or used
  anywhere in the current code — likely the start of an unimplemented
  "pipeline plan" feature. Left in place but unwired; worth finishing or
  removing.
* Only CSV upload is implemented — there's no JSON upload path.
* No Spark — despite the project name, all processing is plain pandas (see
  Future Improvements).

## Fixed in this pass

* `agents/query_agent.py`'s `generate_query_code()` computed a `code`
  variable (with a sane fallback if the LLM returned nothing) and then
  discarded it, re-parsing the raw HTTP response and returning that
  instead — silently bypassing the fallback. Now returns `code` as
  intended.
* `requirements.txt` listed `langchain` and `openai`, neither of which is
  imported anywhere (all LLM calls go to a local Ollama server via plain
  `requests`), while actually missing `requests` and `matplotlib` (both
  used by `backend/services/query_services.py` and the `agents/` modules).
  Replaced the unused entries with the real ones.
* A full Python virtualenv (~18,675 files) and generated upload/output data
  were committed to git with no `.gitignore`. Both are now untracked (kept
  on disk) and gitignored, with `.gitkeep` placeholders so `data/raw` and
  `data/processed` still exist for a fresh clone.

---

## 🚀 Future Improvements

* Time-series analytics engine
* Auto anomaly detection
* Chat-style conversational UI
* SQL + BI dashboard integration
* Support for large-scale datasets (Spark)
* Wire up `pipelines/`/`infra/` or remove them if the fuller platform
  vision is no longer the goal

---

## 💡 Key Learnings

* Combining LLMs with deterministic logic improves reliability
* Data preprocessing is critical for AI performance
* Prompt engineering directly impacts system behavior
* UX design is crucial for AI-driven applications

---

## 👨‍💻 Author

**Jeel Patel**
MS Computer Engineering – New York University

---

## ⭐ If you like this project

Give it a star ⭐ and feel free to contribute!
