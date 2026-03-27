from __future__ import annotations

import requests
import streamlit as st
import pandas as pd

API_BASE_URL = "http://127.0.0.1:8000"

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

    st.subheader("Shapes")
    a, b = st.columns(2)
    a.metric("Original Rows", payload["original_shape"]["rows"])
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