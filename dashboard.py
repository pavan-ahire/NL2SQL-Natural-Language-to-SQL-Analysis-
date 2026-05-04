import streamlit as st
import requests
import pandas as pd
import plotly.io as pio

API_URL = "http://127.0.0.1:8000/chat"

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(
    page_title="IntelliQuery AI Dashboard",
    layout="wide"
)

# ---------------- CUSTOM CSS ---------------- #
st.markdown("""
<style>

/* ---------- MAIN BACKGROUND ---------- */
.stApp {
    background: radial-gradient(circle at top, #0b1220, #020617);
    color: #e2e8f0;
}

/* ---------- HEADER CENTER ---------- */
.main-title {
    text-align: center;
    font-size: 2.6rem;
    font-weight: 700;
    background: linear-gradient(90deg, #7dd3fc, #a78bfa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 5px;
}

.main-sub {
    text-align: center;
    color: #64748b;
    font-size: 14px;
    margin-bottom: 10px;
}

.main-line {
    width: 120px;
    height: 3px;
    background: linear-gradient(90deg, #7dd3fc, #a78bfa);
    margin: 0 auto 25px auto;
    border-radius: 10px;
}

/* ---------- KPI CARDS ---------- */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #0f172a, #020617);
    border: 1px solid rgba(125,211,252,0.15);
    border-radius: 14px;
    padding: 18px;
    box-shadow: 0 0 25px rgba(125,211,252,0.05);
}

/* ---------- SQL BOX ---------- */
.sql-box {
    background: linear-gradient(145deg, #020617, #0f172a);
    border: 1px solid rgba(125,211,252,0.2);
    border-radius: 10px;
    padding: 16px;
    font-family: 'DM Mono', monospace;
    color: #7dd3fc;
    font-size: 13px;
    white-space: pre-wrap;
}

/* ---------- ERROR BOX ---------- */
.error-box {
    background: #2d0b0b;
    border: 1px solid #7f1d1d;
    color: #f87171;
    padding: 12px;
    border-radius: 10px;
}

/* ---------- SUCCESS BOX ---------- */
.success-box {
    background: #022c22;
    border: 1px solid #065f46;
    color: #4ade80;
    padding: 12px;
    border-radius: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ---------------- #
st.sidebar.title("📌 About")

st.sidebar.markdown("""
**IntelliQuery AI** transforms natural language into SQL queries.

### 📊 Database
- Patients  
- Doctors  
- Appointments  
- Treatments  
- Invoices  

### ⚙️ Tech Stack
- Vanna AI 2.0  
- FastAPI  
- SQLite  
- Plotly  

---
### 💡 Try Examples:
""")
st.markdown("""
<style>

[data-testid="stAppViewContainer"] {
    background-color: #0e1117;
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background-color: #111827;
}

</style>
""", unsafe_allow_html=True)

examples = [
    # patients
    "How many patients are registered in the clinic?",
    "List all patients from Mumbai",
    "Show patients with blood group O+",
    "How many male and female patients are there?",
    "Which city has the most patients?",
    # doctors
    "How many doctors are in each department?",
    "Which doctor has the highest consultation fee?",
    "List all cardiologists",
    "Show doctors with more than 10 years of experience",
    "What is the average consultation fee?",
    # appointments
    "How many appointments were completed?",
    "Show appointment count by status",
    "Which doctor has the most appointments?",
    "How many appointments were cancelled?",
    "List appointments scheduled for 2024",
    # treatments & revenue
    "What are the most common diagnoses?",
    "What is the total cost of all treatments?",
    "What is the total revenue collected by the clinic?",
    "Show revenue by payment method",
    "How many invoices are pending payment?",
]

selected_query = None
for q in examples:
    if st.sidebar.button(q):
        selected_query = q

# ---------------- HEADER ---------------- #
st.markdown('<div class="main-title">🧠 IntelliQuery AI</div>', unsafe_allow_html=True)
st.markdown('<div class="main-sub">AI-powered Natural Language to SQL Analytics Platform</div>', unsafe_allow_html=True)
st.markdown('<div class="main-line"></div>', unsafe_allow_html=True)
st.markdown("""
Ask questions in plain English and instantly get:
- Structured data  
- SQL queries  
- Visual insights  
""")

st.markdown("---")

# ---------------- INPUT ---------------- #
question = st.text_input(
    "",
    value=selected_query if selected_query else "",
    placeholder="Ask something like: Show top 5 patients by spending..."
)

ask = st.button("🚀 Generate Insight")

# ---------------- RESPONSE ---------------- #
if ask:

    if not question.strip():
        st.warning("Please enter a question.")
        st.stop()

    with st.spinner("Analyzing..."):
        try:
            response = requests.post(API_URL, json={"question": question})
            data = response.json()
        except:
            st.error("Backend not running.")
            st.stop()

    if response.status_code != 200:
        st.error("API error occurred.")
        st.stop()

    st.markdown("---")

    # ---------------- AI RESPONSE ---------------- #
    st.subheader("💬 AI Insight")
    st.success(data.get("message", "No response"))

    # ---------------- KPIs ---------------- #
    col1, col2, col3 = st.columns(3)

    col1.metric("Rows", data.get("row_count", 0))
    col2.metric("Columns", len(data.get("columns", [])))
    col3.metric("Status", "Success")

    # ---------------- TABLE ---------------- #
    if data.get("rows"):
        df = pd.DataFrame(data["rows"], columns=data["columns"])
        st.markdown("### 📊 Data")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available.")

    # # ---------------- CHART ---------------- #
    # if data.get("chart_json"):
    #     st.markdown("### 📈 Visualization")
    #     try:
    #         fig = pio.from_json(data["chart"])
    #         st.plotly_chart(fig, use_container_width=True)
    #     except:
    #         st.warning("Chart could not be rendered.")

    # ---------------- SQL (FIXED ISSUE) ---------------- #
    st.markdown("### 🧾 Generated SQL")

    sql_query = data.get("sql")

    if sql_query:
        st.code(sql_query, language="sql")
    else:
        st.info("SQL not available (agent did not return it).")

# ---------------- FOOTER ---------------- #
st.markdown("---")
st.caption("🚀 Built with IntelliQuery AI | Natural Language → SQL → Insights")