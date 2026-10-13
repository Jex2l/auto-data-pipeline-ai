from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="AI Data Engineer",
    page_icon="🧪",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
    }
    .adp-card {
        background-color: rgba(127, 127, 127, 0.07);
        border: 1px solid rgba(127, 127, 127, 0.18);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1rem;
    }
    .adp-status-ok {
        color: #1a7f37;
        font-weight: 600;
    }
    .adp-status-bad {
        color: #c0392b;
        font-weight: 600;
    }
    div[data-testid="stMetric"] {
        background-color: rgba(127, 127, 127, 0.07);
        border: 1px solid rgba(127, 127, 127, 0.18);
        border-radius: 10px;
        padding: 0.6rem 0.8rem 0.3rem 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧪 AI Data Engineer")
st.caption(
    "Upload a CSV, let the pipeline clean it, inspect the schema, review "
    "quick insights, and ask questions about your data in plain English."
)

if "last_result" not in st.session_state:
    st.session_state.last_result = None

# ---------------------------------------------------------------------------
# Step 1 — Upload & process
# ---------------------------------------------------------------------------
st.header("1️⃣ Upload your dataset", divider="gray")

uploaded_file = st.file_uploader(
    "Upload a CSV file (max 25MB)",
    type=["csv"],
    help="Only .csv files are accepted for this MVP.",
)

action_col1, action_col2 = st.columns([1, 1])

with action_col1:
    process_clicked = st.button(
        "🚀 Process File",
        disabled=uploaded_file is None,
        use_container_width=True,
    )

with action_col2:
    clear_clicked = st.button("🗑️ Clear Results", use_container_width=True)

if clear_clicked:
    st.session_state.last_result = None
    st.rerun()

if process_clicked:
    if uploaded_file is None:
        st.warning("Please upload a CSV file first.")
    else:
        files = {
            "file": (
                uploaded_file.name,
                uploaded_file.getvalue(),
                "text/csv",
            )
        }

        try:
            with st.spinner("Uploading and processing your dataset..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/upload",
                    files=files,
                    timeout=120,
                )
                response.raise_for_status()
                st.session_state.last_result = response.json()
            st.success("✅ File processed successfully.")
        except requests.HTTPError:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            st.error(f"API error: {detail}")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not reach the backend at "
                f"`{API_BASE_URL}`. Is `uvicorn backend.main:app --reload` running?"
            )
        except Exception as exc:
            st.error(f"Request failed: {exc}")

result = st.session_state.last_result

if not result:
    st.info("👆 Upload a CSV and click **Process File** to get started.")
    st.stop()

payload = result.get("result", {})

if not isinstance(payload, dict):
    st.error("Invalid response from backend.")
    st.stop()

if payload.get("status") == "error":
    st.error(payload.get("error", "Unknown backend error"))
    st.stop()

# ---------------------------------------------------------------------------
# Step 2 — Shapes, schema, cleaning, insights
# ---------------------------------------------------------------------------
st.header("2️⃣ Cleaning & schema report", divider="gray")

original_shape = payload.get("original_shape", {})
cleaned_shape = payload.get("cleaned_shape", {})

shape_col1, shape_col2 = st.columns(2)

with shape_col1:
    st.markdown("**Before cleaning**")
    inner_col1, inner_col2 = st.columns(2)
    inner_col1.metric("Rows", original_shape.get("rows", "N/A"))
    inner_col2.metric("Columns", original_shape.get("columns", "N/A"))

with shape_col2:
    st.markdown("**After cleaning**")
    inner_col1, inner_col2 = st.columns(2)
    inner_col1.metric("Rows", cleaned_shape.get("rows", "N/A"))
    inner_col2.metric("Columns", cleaned_shape.get("columns", "N/A"))

with st.expander("🧹 Cleaning report", expanded=True):
    st.json(payload.get("cleaning_report", {}))

schema_before_col, schema_after_col = st.columns(2)

with schema_before_col:
    with st.expander("📋 Schema before cleaning"):
        st.json(payload.get("schema_before", {}))

with schema_after_col:
    with st.expander("📋 Schema after cleaning"):
        st.json(payload.get("schema_after", {}))

st.subheader("📈 Insights")
with st.container():
    st.json(payload.get("insights", {}))

st.subheader("👀 Preview")
preview = payload.get("preview", [])
preview_df = pd.DataFrame(preview)
if preview_df.empty:
    st.info("No preview rows available.")
else:
    st.dataframe(preview_df, use_container_width=True)

with st.expander("🗂️ Summary"):
    st.json(payload.get("summary", {}))

# ---------------------------------------------------------------------------
# Step 3 — AI analysis & suggested SQL
# ---------------------------------------------------------------------------
st.header("3️⃣ AI analysis", divider="gray")

st.markdown('<div class="adp-card">', unsafe_allow_html=True)
st.markdown("**🤖 AI Analysis**")
st.write(payload.get("llm_analysis", "No AI analysis available."))
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("**🗄️ Generated SQL Queries**")
sql_queries = payload.get("sql_queries")
if sql_queries:
    if isinstance(sql_queries, list):
        st.code("\n\n".join(sql_queries), language="sql")
    else:
        st.code(str(sql_queries), language="sql")
else:
    st.info("No SQL queries generated.")

# ---------------------------------------------------------------------------
# Step 4 — Ask questions
# ---------------------------------------------------------------------------
st.header("4️⃣ Ask questions about your data", divider="gray")
st.caption(
    "A local LLM translates your question into pandas code and runs it "
    "against the cleaned dataset."
)

question = st.text_input(
    "Ask something about your dataset",
    placeholder="e.g. What is the average volume?",
)
ask_clicked = st.button("💬 Ask")

if ask_clicked:
    if not question.strip():
        st.warning("Please enter a question first.")
    else:
        try:
            with st.spinner("Thinking..."):
                response = requests.post(
                    f"{API_BASE_URL}/api/ask",
                    json={"question": question},
                    timeout=120,
                )
                response.raise_for_status()
                data = response.json()

            if not data.get("success"):
                st.error(data.get("error", "Unknown error"))
            else:
                st.markdown("**📊 Insight**")
                result_text = data.get("result", "")

                if "Error" in result_text or "invalid syntax" in result_text:
                    st.error(
                        "⚠️ Failed to generate a valid answer. Try rephrasing "
                        "your question."
                    )
                else:
                    st.success(result_text)

                if data.get("image"):
                    st.markdown("**📈 Visualization**")
                    st.image(f"data:image/png;base64,{data['image']}")

                with st.expander("🔎 Generated code"):
                    st.code(data.get("generated_code") or "", language="python")

        except requests.HTTPError:
            try:
                detail = response.json().get("detail", response.text)
            except Exception:
                detail = response.text
            st.error(f"API error: {detail}")
        except requests.exceptions.ConnectionError:
            st.error(
                "Could not reach the backend at "
                f"`{API_BASE_URL}`. Is `uvicorn backend.main:app --reload` running?"
            )
        except Exception as exc:
            st.error(f"Request failed: {exc}")

# ---------------------------------------------------------------------------
# Step 5 — Quick visualizations
# ---------------------------------------------------------------------------
st.header("5️⃣ Quick visualizations", divider="gray")

if preview_df.empty:
    st.info("No data available to chart.")
else:
    chart_df = preview_df.copy()

    # Clean column names
    chart_df.columns = [col.strip().lower() for col in chart_df.columns]

    # Force numeric conversion for charting purposes only
    for col in chart_df.columns:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    numeric_cols = chart_df.select_dtypes(include=["number"]).columns.tolist()

    if numeric_cols:
        selected_col = st.selectbox("Select a column to visualize", numeric_cols)

        st.markdown(f"**📈 {selected_col}**")
        col_data = chart_df[selected_col].dropna()

        if col_data.empty:
            st.warning(f"No valid data to plot for '{selected_col}'.")
        else:
            st.line_chart(col_data.reset_index(drop=True))
    else:
        st.error("❌ No numeric columns detected. Check dataset formatting.")
