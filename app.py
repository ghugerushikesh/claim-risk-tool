import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2
from sklearn.ensemble import RandomForestClassifier

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Smart Claim Analyzer", page_icon="🛡️", layout="wide")

# ---------------- LOGIN SYSTEM ----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🔐 Smart Claim Analyzer Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("Invalid credentials")

    st.stop()

# ---------------- CUSTOM CSS ----------------
st.markdown("""
<style>
.stApp { background-color: #0E1117; color: white; }
[data-testid="stSidebar"] { background-color: #12151E; }
</style>
""", unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🛠️ Smart Claim Tool")
    page = st.radio("Navigation", ["Dashboard", "Upload Data", "PDF Reader"])

# ---------------- HEADER ----------------
st.markdown("""
<h1 style='text-align:center;'>🛡️ Smart Claim Analyzer</h1>
<p style='text-align:center;color:gray;'>AI-powered Claim Risk & Fraud Detection</p>
""", unsafe_allow_html=True)

st.divider()

# ---------------- FUNCTIONS ----------------
def calculate_risk(row):
    score = 0
    if row.get("Amount", 0) > 200000:
        score += 2
    if row.get("Previous_Claims", 0) >= 2:
        score += 1
    if row.get("Hospital", "") == "B":
        score += 1

    if score >= 3:
        return "High Risk"
    elif score == 2:
        return "Medium Risk"
    else:
        return "Low Risk"

def decision(risk):
    return "Manual Review" if risk == "High Risk" else "Auto Approve"

# ---------------- UPLOAD ----------------
if page == "Upload Data":
    st.header("📤 Upload Claim Data")

    file = st.file_uploader("Upload CSV", type=["csv"])

    if file:
        df = pd.read_csv(file)

        if not df.empty:
            df["Risk"] = df.apply(calculate_risk, axis=1)
            df["Decision"] = df["Risk"].apply(decision)

            # ML MODEL
            if all(col in df.columns for col in ["Amount", "Previous_Claims"]):
                df["Risk_Label"] = df["Risk"].map({
                    "Low Risk": 0,
                    "Medium Risk": 1,
                    "High Risk": 2
                })

                X = df[["Amount", "Previous_Claims"]]
                y = df["Risk_Label"]

                model = RandomForestClassifier()
                model.fit(X, y)

                df["Predicted_Risk"] = model.predict(X)

                mapping = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
                df["Predicted_Risk"] = df["Predicted_Risk"].map(mapping)

            st.session_state["data"] = df

            st.success("Data processed successfully")
            st.dataframe(df, use_container_width=True)

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    st.header("📊 Dashboard")

    if "data" not in st.session_state:
        st.warning("Upload data first")
    else:
        df = st.session_state["data"]

        col1, col2, col3 = st.columns(3)

        total = len(df)
        high = (df["Risk"] == "High Risk").sum()
        auto = (df["Decision"] == "Auto Approve").sum()

        col1.metric("Total Claims", total)
        col2.metric("High Risk", high)
        col3.metric("Auto Approvals", auto)

        # Business Value
        fraud_loss = high * 50000
        st.metric("Potential Fraud Exposure", f"₹{fraud_loss:,.0f}")

        if high > 0:
            st.error("High Risk Claims Detected")
        else:
            st.success("All claims safe")

        # Charts
        risk_counts = df["Risk"].value_counts()

        st.subheader("Bar Chart")
        st.bar_chart(risk_counts)

        st.subheader("Pie Chart")
        fig, ax = plt.subplots()
        risk_counts.plot.pie(autopct="%1.1f%%", ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)

        # Filter
        risk_filter = st.selectbox("Filter Risk", ["All", "Low Risk", "Medium Risk", "High Risk"])

        if risk_filter != "All":
            df = df[df["Risk"] == risk_filter]

        st.dataframe(df, use_container_width=True)

# ---------------- PDF ----------------
elif page == "PDF Reader":
    st.header("📄 PDF Reader")

    pdf = st.file_uploader("Upload PDF", type=["pdf"])

    if pdf:
        reader = PyPDF2.PdfReader(pdf)
        text = ""

        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content

        st.text_area("Extracted Text", text, height=300)

        st.download_button("Download Text", text, file_name="output.txt")
