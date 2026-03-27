from __future__ import annotations

import pandas as pd
import requests
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="AI Data Engineer", layout="wide")
st.title("AI Data Engineer MVP")
st.caption("Upload a CSV, clean it, inspect schema, and review quick insights.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

top_col1, top_col2 = st.columns([1, 1])

with top_col1:
    if st.button("Process File", disabled=uploaded_file is None):
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
                with st.spinner("Uploading and processing..."):
                    response = requests.post(
                        f"{API_BASE_URL}/api/upload",
                        files=files,
                        timeout=120,
                    )
                    response.raise_for_status()
                    st.session_state.last_result = response.json()
                    st.success("File processed successfully.")
            except requests.HTTPError:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                st.error(f"API error: {detail}")
            except Exception as exc:
                st.error(f"Request failed: {exc}")

with top_col2:
    if st.button("Clear Results"):
        st.session_state.last_result = None
        st.rerun()

result = st.session_state.last_result

if result:
    payload = result.get("result", {})

    if not isinstance(payload, dict):
        st.error("Invalid response from backend.")
        st.stop()

    if payload.get("status") == "error":
        st.error(payload.get("error", "Unknown backend error"))
        st.stop()

    st.subheader("Shapes")
    shape_col1, shape_col2 = st.columns(2)

    original_shape = payload.get("original_shape", {})
    cleaned_shape = payload.get("cleaned_shape", {})

    with shape_col1:
        st.metric("Original Rows", original_shape.get("rows", "N/A"))
        st.metric("Original Columns", original_shape.get("columns", "N/A"))

    with shape_col2:
        st.metric("Cleaned Rows", cleaned_shape.get("rows", "N/A"))
        st.metric("Cleaned Columns", cleaned_shape.get("columns", "N/A"))

    st.subheader("Cleaning Report")
    st.json(payload.get("cleaning_report", {}))

    st.subheader("Schema Before Cleaning")
    st.json(payload.get("schema_before", {}))

    st.subheader("Schema After Cleaning")
    st.json(payload.get("schema_after", {}))

    st.subheader("Insights")
    st.json(payload.get("insights", {}))

    st.subheader("Preview")
    preview = payload.get("preview", [])
    preview_df = pd.DataFrame(preview)
    st.dataframe(preview_df, use_container_width=True)

    st.subheader("Summary")
    st.json(payload.get("summary", {}))

    st.subheader("AI Analysis")
    st.write(payload.get("llm_analysis", "No AI analysis available."))

    st.subheader("Generated SQL Queries")
    sql_queries = payload.get("sql_queries")
    if sql_queries:
        if isinstance(sql_queries, list):
            st.code("\n\n".join(sql_queries), language="sql")
        else:
            st.code(str(sql_queries), language="sql")
    else:
        st.info("No SQL queries generated.")

    st.subheader("Ask Questions About Your Data")
    question = st.text_input("Ask something about your dataset")

    if st.button("Ask"):
        if not question.strip():
            st.warning("Please enter a question first.")
        else:
            try:
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
                    st.subheader("📊 Insight")
                    result_text = data.get("result", "")

                    if "Error" in result_text or "invalid syntax" in result_text:
                        st.error("⚠️ Failed to generate valid answer. Try rephrasing your question.")
                    else:
                        st.success(result_text)

                    if data.get("image"):
                        st.subheader("Visualization")
                        st.image(f"data:image/png;base64,{data['image']}")

            except requests.HTTPError:
                try:
                    detail = response.json().get("detail", response.text)
                except Exception:
                    detail = response.text
                st.error(f"API error: {detail}")
            except Exception as exc:
                st.error(f"Request failed: {exc}")

    st.subheader("📊 Quick Visualizations")

    if not preview_df.empty:

        # ✅ CLEAN COLUMN NAMES
        preview_df.columns = [col.strip().lower() for col in preview_df.columns]

        # ✅ FORCE NUMERIC CONVERSION
        for col in preview_df.columns:
            preview_df[col] = pd.to_numeric(preview_df[col], errors='coerce')

        numeric_cols = preview_df.select_dtypes(include=["number"]).columns.tolist()

        if numeric_cols:

            selected_col = st.selectbox(
                "Select a column to visualize",
                numeric_cols
            )

            st.markdown(f"### 📈 {selected_col}")
            col_data = preview_df[selected_col].dropna()

            if col_data.empty:
                st.warning(f"No valid data to plot for '{selected_col}'")
            else:
                chart_df = col_data.reset_index(drop=True)
                st.line_chart(chart_df)

        else:
            st.error("❌ No numeric columns detected. Check dataset formatting.")
    else:
        st.info("No data available.")