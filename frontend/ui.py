import streamlit as st
import requests
import pandas as pd

API_BASE = "http://localhost:8000"

st.set_page_config(page_title="Dumroo AI Admin Panel", layout="wide")


st.sidebar.title("📊 Previous Queries")
admin_id = st.sidebar.number_input("Admin ID", min_value=1, value=1, step=1)
query_history = requests.get(f"{API_BASE}/queries/{admin_id}")

selected_query = None
if query_history.status_code == 200:
    queries = query_history.json()
    for i, q in enumerate(queries):
        if st.sidebar.button(q["title"], key=i):
            selected_query = q["id"]
else:
    st.sidebar.info("No previous queries found.")


st.markdown("## Dumroo AI Admin Panel")


question = st.text_input("Ask a question about your data...")
if st.button("Ask"):
    if question:
        response = requests.post(f"{API_BASE}/ask", params={"question": question, "admin_id": admin_id})
        if response.status_code == 200:
            selected_query = response.json()["sql"]
        else:
            st.error(response.json()["detail"])

if selected_query:
    if isinstance(selected_query, int):
        qres = requests.get(f"{API_BASE}/query/{selected_query}")
        question= qres.json().get(question)
        if qres.status_code == 200:
            data = qres.json()
        else:
            st.error("Failed to load query result.")
            st.stop()
    else:
        data = response.json()


    col1, col2 = st.columns([1.0, 2.0])

    with col1:
        # table for data
        st.markdown("### 📋 Data Table")
        df = pd.DataFrame(data["data"])
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Export CSV", csv, "query_data.csv", "text/csv")
        st.dataframe(df)

           
        st.markdown("#### 🧠 SQL Query")
        st.code(data["sql"], language="sql")

    with col2:
        st.markdown("#### 💡 AI Insights")
        st.info(data["insights"])
        # chart
        st.markdown("### 📊 Chart Visualization")
        if "chart_url" in data and data["chart_url"]:
            chart_full_url = f'http://localhost:8000/static{data["chart_url"]}'
            st.components.v1.html(
            f'''
            <div style="position:relative;">
                <iframe src="{chart_full_url}" width="100%" height="500" frameborder="0"></iframe>
                <a href="{chart_full_url}" target="_blank" style="position:absolute;top:10px;right:10px;z-index:10;padding:6px 12px;background:#0366d6;color:#fff;border-radius:4px;text-decoration:none;font-size:14px;">🔎 Full Screen</a>
            </div>
            ''',
            height=520
            )
        else:
            st.info("No chart available for this query.")


 