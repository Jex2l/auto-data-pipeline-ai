# 🚀 Auto Data Pipeline AI

An AI-powered data engineering assistant that automates data ingestion, cleaning, analysis, visualization, and querying — all through a simple UI.

---

## 📌 Overview

Auto Data Pipeline AI is a full-stack application that allows users to:

* Upload raw CSV datasets
* Automatically clean and preprocess data
* Generate schema summaries and insights
* Visualize data instantly
* Ask natural language questions about the dataset
* Get answers powered by AI + Python execution

This project bridges the gap between **data engineering, analytics, and AI**, enabling non-technical users to interact with data like a data scientist.

---

## 🧠 Key Features

### 📂 Data Ingestion

* Upload CSV files through Streamlit UI
* File validation and size checks
* Automatic storage and processing

### 🧹 Data Cleaning

* Missing value handling
* Data type normalization
* Column name standardization
* Cleaning report generation

### 📊 Data Insights

* Schema inference before and after cleaning
* Basic statistical insights
* Missing value summaries

### 📈 Visualization

* Automatic detection of numeric columns
* Interactive dropdown-based visualization
* Dynamic charts using Streamlit

### 🤖 AI Query Engine

* Ask questions in natural language
* LLM converts query → Python (Pandas)
* Executes code safely and returns results
* Optional visualization generation

---

## 🏗️ Architecture

```
Frontend (Streamlit)
        ↓
FastAPI Backend
        ↓
Data Processing Layer (Pandas)
        ↓
AI Agents (LLM + Rule-based logic)
```

---

## 🛠️ Tech Stack

### 🔹 Frontend

* Streamlit

### 🔹 Backend

* FastAPI
* Uvicorn

### 🔹 Data Processing

* Pandas
* NumPy

### 🔹 AI / LLM

* OpenAI / Gemini (via custom agents)
* Prompt-engineered query generation

### 🔹 Visualization

* Streamlit charts
* Matplotlib (for generated plots)

---

## 📂 Project Structure

```
auto-data-pipeline-ai/
│
├── backend/
│   ├── main.py
│   ├── routes/
│   │   ├── upload.py
│   │   ├── query.py
│   │
│   ├── services/
│   │   ├── data_service.py
│   │   ├── query_services.py
│
├── agents/
│   ├── cleaning_agent.py
│   ├── query_agent.py
│   ├── insight_agent.py
│   ├── schema_agent.py
│   ├── llm_agent.py
│
├── frontend/
│   └── app.py
│
├── data/
│   ├── raw/
│   ├── processed/
│
└── README.md
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Jex2l/auto-data-pipeline-ai.git
cd auto-data-pipeline-ai
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

---

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Run Backend

```bash
python uvicorn backend.main:app --reload
```

Backend runs at:

```
http://127.0.0.1:8000
```

---

### 5️⃣ Run Frontend

```bash
streamlit run frontend/app.py
```

---

## 📊 How It Works

### Step 1: Upload Dataset

* User uploads CSV
* Backend saves and processes file

### Step 2: Data Processing

* Cleans dataset
* Converts data types
* Generates insights

### Step 3: Visualization

* Detects numeric columns
* Displays interactive charts

### Step 4: Ask Questions

* User asks natural language question
* LLM generates Pandas code
* Backend executes code
* Result returned to UI

---

## 🧪 Example Queries

### ✅ Supported

* What is the average volume?
* What is the minimum close value?
* Show top 5 highest values
* What is the total volume?

### ❌ Not Recommended (LLM limitation)

* Longest increasing streak
* Complex time-series patterns
* Multi-step logical reasoning

---

## 🔒 Error Handling

* Invalid file formats rejected
* Safe execution of generated code
* Graceful fallback for LLM failures
* UI-level error feedback

---

## 🚀 Future Improvements

* Time-series analytics engine
* Auto anomaly detection
* Chat-style conversational UI
* SQL + BI dashboard integration
* Support for large-scale datasets (Spark)

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

---
