import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2
from sklearn.ensemble import RandomForestClassifier

st.set_page_config(page_title="Smart Claim Analyzer", layout="wide")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🛠️ Smart Claim Tool")
page = st.sidebar.radio("Navigation", ["Dashboard", "Upload Data", "PDF Reader"])

st.title("🛡️ Smart Claim Analyzer")
st.markdown("### AI-powered Claim Risk & Fraud Detection System")
st.divider()

# ---------------- UPLOAD DATA ----------------
if page == "Upload Data":
    st.header("📤 Upload Claim Data")

    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.subheader("📊 Raw Data")
        st.dataframe(df)

        # ---------------- RISK LOGIC ----------------
        def calculate_risk(row):
            score = 0

            if row["Amount"] > 200000:
                score += 2
            if row["Previous_Claims"] >= 2:
                score += 1
            if row["Hospital"] == "B":
                score += 1

            if score >= 3:
                return "High Risk"
            elif score == 2:
                return "Medium Risk"
            else:
                return "Low Risk"

        df["Risk"] = df.apply(calculate_risk, axis=1)

        # ---------------- DECISION ----------------
        def decision(risk):
            if risk == "High Risk":
                return "Manual Review"
            else:
                return "Auto Approve"

        df["Decision"] = df["Risk"].apply(decision)

        # ---------------- ML MODEL ----------------
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

        risk_map = {0: "Low Risk", 1: "Medium Risk", 2: "High Risk"}
        df["Predicted_Risk"] = df["Predicted_Risk"].map(risk_map)

        st.success("✅ Data processed successfully!")

        # Save in session for dashboard
        st.session_state["data"] = df

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    st.header("📊 Dashboard")

    if "data" not in st.session_state:
        st.warning("⚠️ Please upload data first")
    else:
        df = st.session_state["data"]

        st.subheader("📌 Summary")

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Claims", len(df))
        col2.metric("High Risk", (df["Risk"] == "High Risk").sum())
        col3.metric("Auto Approvals", (df["Decision"] == "Auto Approve").sum())

        # Alerts
        if (df["Risk"] == "High Risk").sum() > 0:
            st.error("⚠️ High Risk Claims Detected!")
        else:
            st.success("✅ All claims look safe")

        # Charts
        st.subheader("📈 Risk Distribution")

        risk_counts = df["Risk"].value_counts()
        st.bar_chart(risk_counts)

        # Pie Chart
        st.subheader("🥧 Risk Share")

        fig, ax = plt.subplots()
        risk_counts.plot.pie(autopct="%1.1f%%", ax=ax)
        ax.set_ylabel("")
        st.pyplot(fig)

        # Filter
        st.subheader("🔍 Filter Data")

        risk_filter = st.selectbox(
            "Select Risk Level",
            ["All", "Low Risk", "Medium Risk", "High Risk"]
        )

        if risk_filter != "All":
            filtered_df = df[df["Risk"] == risk_filter]
        else:
            filtered_df = df

        st.dataframe(filtered_df)

# ---------------- PDF READER ----------------
elif page == "PDF Reader":
    st.header("📄 Claim PDF Reader")

    pdf_file = st.file_uploader("Upload PDF File", type=["pdf"])

    if pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""

        for page in reader.pages:
            text += page.extract_text()

        st.subheader("📄 Extracted Text")
        st.write(text)

        st.info("👉 You can later extract amount, hospital, etc. from this text")
