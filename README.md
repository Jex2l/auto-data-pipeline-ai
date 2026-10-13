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

## 📑 Table of Contents

* [Overview](#-overview)
* [Key Features](#-key-features)
* [Architecture](#️-architecture)
* [Tech Stack](#️-tech-stack)
* [Project Structure](#-project-structure)
* [Installation & Setup](#️-installation--setup)
* [How It Works](#-how-it-works)
* [Error Handling](#-error-handling)
* [Known Limitations](#known-limitations)
* [Fixed in This Pass](#fixed-in-this-pass)
* [Future Improvements](#-future-improvements)
* [Key Learnings](#-key-learnings)
* [Author](#-author)

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

The Streamlit UI never talks to pandas, Ollama, or the filesystem directly —
every data operation goes through the FastAPI backend, which in turn calls
plain-function "agents" for each step of the pipeline.

```
┌───────────────────┐        ┌───────────────────────────┐        ┌──────────────────────────────┐
│   Streamlit UI     │  HTTP  │        FastAPI backend      │  calls │        agents/ (plain fns)     │
│  frontend/app.py   │ ─────► │   backend/routes/*.py +     │ ─────► │ schema_agent, cleaning_agent,  │
│                     │        │   backend/services/*.py    │        │ insight_agent, llm_agent,      │
└───────────────────┘        └───────────────────────────┘        │ sql_agent, query_agent          │
                                                                     └──────────────────────────────┘

Upload flow  (POST /api/upload, a CSV file)
  routes/upload.py → services/data_service.process_uploaded_csv()
    1. pandas reads the CSV
    2. schema_agent.infer_schema_summary()   → schema BEFORE cleaning
    3. cleaning_agent.clean_dataframe()      → dedup, normalize columns,
                                                 null-token cleanup, numeric
                                                 coercion
    4. schema_agent.infer_schema_summary()   → schema AFTER cleaning
    5. insight_agent.generate_basic_insights() → numeric/categorical stats
    6. llm_agent.analyze_dataset()           → asks Ollama for a prose
                                                 summary of the cleaned data
    7. sql_agent.generate_sql()              → asks Ollama for 3 example
                                                 SQL queries
    → cleaned CSV + JSON report written to data/processed/
    → cleaned dataframe kept in-memory as the "current dataset"
      (backend.routes.query.GLOBAL_DF)

Ask flow  (POST /api/ask, a natural-language question)
  routes/query.py → agents/query_agent.generate_query_code()
    asks the local Ollama server to turn the question into pandas code
    that stores its answer in a `result` variable
  → services/query_services.execute_query()
    runs that code via exec() against the in-memory dataframe, captures
    any matplotlib figure it produced, and returns (result, chart PNG)
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

### What each piece does

**`backend/`**
* `main.py` — creates the FastAPI app, enables permissive CORS, and mounts
  the upload and query routers under `/api`.
* `routes/upload.py` — `/api/upload` endpoint: validates the file is a CSV
  under 25MB, saves it under `data/raw/`, runs it through
  `data_service.process_uploaded_csv()`, and stashes the cleaned dataframe
  for later questions.
* `routes/query.py` — `/api/ask` endpoint: holds the in-memory
  `GLOBAL_DF`, generates pandas code for the question via
  `agents.query_agent`, and runs it via `query_services.execute_query()`.
* `services/data_service.py` — orchestrates the full upload pipeline
  (read CSV → schema before → clean → schema after → insights → LLM
  analysis → SQL suggestions), writes the cleaned CSV + JSON report to
  `data/processed/`.
* `services/query_services.py` — executes LLM-generated pandas code
  against the dataframe with `exec()`, captures a matplotlib figure if one
  was drawn, and returns it as a base64 PNG.

**`agents/`**
* `schema_agent.py` — `infer_schema_summary()`: per-column dtype, null
  counts, unique counts, and a few sample values.
* `cleaning_agent.py` — `clean_dataframe()`: normalizes column names,
  strips whitespace, replaces common null tokens (`"n/a"`, `"null"`, …),
  coerces numeric-looking columns, drops duplicate/empty rows and columns,
  and returns a before/after report.
* `insight_agent.py` — `generate_basic_insights()`: min/max/mean/median for
  up to 10 numeric columns and top-5 value counts for up to 10 categorical
  columns.
* `llm_agent.py` — `analyze_dataset()`: sends a sample of the cleaned data
  to the local Ollama server and asks for a prose summary (what the data
  represents, patterns, quality issues, next steps).
* `sql_agent.py` — `generate_sql()`: asks Ollama for 3 example SQL queries
  based on the dataset's column names.
* `query_agent.py` — `generate_query_code()`: turns a natural-language
  question into pandas code (storing the answer in a `result` variable),
  with a `result = df.head()` fallback if Ollama returns nothing.
* `pipeline_agent.py` *(unwired, see Known limitations)* —
  `generate_pandas_pipeline_code()` / `save_generated_pipeline()`: would
  generate a standalone pandas script that deduplicates and projects a
  fixed column list.
* `utils.py` *(unwired, see Known limitations)* — `ensure_dir()`: a
  one-line `mkdir -p` helper.

**`frontend/app.py`** — the entire Streamlit UI: file upload, a "Process
File" / "Clear Results" action pair, rendering of shapes/schema/insights/
preview/AI analysis/SQL, a question box for `/api/ask`, and a quick
line-chart visualizer over the preview rows.

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
