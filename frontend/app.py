from __future__ import annotations

import requests
import streamlit as st
import pandas as pd

url = "http://127.0.0.1:8000/process"

st.set_page_config(page_title="AI Data Engineer", layout="wide")
st.title("AI Data Engineer MVP")
st.caption("Upload a CSV, clean it, inspect schema, and review quick insights.")

if "last_result" not in st.session_state:
    st.session_state.last_result = None

uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

col1, col2 = st.columns([1, 1])

with col1:
    if st.button("Process File", disabled=uploaded_file is None):
        if uploaded_file is None:
            st.warning("Please upload a CSV file first.")
        else:
            files = {
                "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
            }
            try:
                with st.spinner("Uploading and processing..."):
                    response = requests.post(f"{API_BASE_URL}/api/upload", files=files, timeout=120)
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

with col2:
    if st.button("Clear Results"):
        st.session_state.last_result = None
        st.rerun()

result = st.session_state.last_result

if result:
    payload = result["result"]
    st.subheader("Ask Questions About Your Data")

    question = st.text_input("Ask something about your dataset")

    if st.button("Ask"):
        response = requests.post(
            "http://127.0.0.1:8000/api/ask",
            json={"question": question}
        )

        data = response.json()

        # 🧠 Handle failure first
        if not data.get("success"):
            st.error(data.get("error", "Unknown error"))
            st.stop()

        # 🔍 Debug (optional)
        # st.write(data)

        # 🧠 Generated Code
        if data.get("generated_code"):
            st.subheader("Generated Code")
            st.code(data["generated_code"])
        else:
            st.warning("No code generated.")

        # 🧠 Result
        st.subheader("Answer")
        st.write(data.get("result", "No result returned"))

        # 🧠 Image
        if data.get("image"):
            st.subheader("Visualization")
            st.image(f"data:image/png;base64,{data['image']}")
    st.subheader("Shapes")
    a, b = st.columns(2)
    if not isinstance(payload, dict):
        st.error("Invalid response from backend")

    elif payload.get("status") == "error":
        st.error(payload.get("error", "Unknown error"))

    else:
        original_shape = payload.get("original_shape", {})
        cleaned_shape = payload.get("cleaned_shape", {})

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Original Rows",
                original_shape.get("rows", "N/A")
            )

        with col2:
            st.metric(
                "Cleaned Rows",
                cleaned_shape.get("rows", "N/A")
            )
    a.metric("Original Columns", payload["original_shape"]["columns"])
    b.metric("Cleaned Rows", payload["cleaned_shape"]["rows"])
    b.metric("Cleaned Columns", payload["cleaned_shape"]["columns"])

    st.subheader("Cleaning Report")
    st.json(payload["cleaning_report"])

    st.subheader("Schema After Cleaning")
    st.json(payload["schema_after"])

    st.subheader("Insights")
    st.json(payload["insights"])

    st.subheader("Preview")
    preview_df = pd.DataFrame(payload["preview"])
    st.dataframe(preview_df, use_container_width=True)

    st.subheader("AI Analysis")

    if "llm_analysis" in payload:
        st.write(payload["llm_analysis"])

    st.subheader("Quick Visualizations")

    df = pd.DataFrame(payload["preview"])
    if data.get("image"):
        st.image(f"data:image/png;base64,{data['image']}")
    numeric_cols = df.select_dtypes(include=['number']).columns

    if len(numeric_cols) > 0:
        col = numeric_cols[0]
        st.write(f"Distribution of {col}")
        st.bar_chart(df[col])
    else:
        st.info("No numeric columns available for chart.")

    st.subheader("Generated SQL Queries")

    if "sql_queries" in payload:
        st.code(payload["sql_queries"], language="sql")