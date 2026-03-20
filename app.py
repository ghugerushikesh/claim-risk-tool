import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2

st.set_page_config(page_title="Claim Risk Tool", layout="wide")

st.title("🛡️ Claim Risk Scoring Dashboard")

# 📤 CSV Upload
uploaded_file = st.file_uploader("📤 Upload Claim CSV File", type=["csv"])

# 📄 PDF Upload
pdf_file = st.file_uploader("📄 Upload Claim PDF", type=["pdf"])

# ---------------- PDF SECTION ----------------
if pdf_file:
    reader = PyPDF2.PdfReader(pdf_file)
    text = ""

    for page in reader.pages:
        text += page.extract_text()

    st.subheader("📄 Extracted Text from PDF")
    st.write(text)

# ---------------- CSV SECTION ----------------
if uploaded_file:
    df = pd.read_csv(uploaded_file)

    st.subheader("📊 Raw Data")
    st.dataframe(df)

    # 🧠 Smart Risk Scoring (Improved Logic)
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

    # 🧠 Decision Logic
    def decision(risk):
        if risk == "High Risk":
            return "Manual Review"
        else:
            return "Auto Approve"

    df["Decision"] = df["Risk"].apply(decision)

    # ✅ Processed Data
    st.subheader("✅ Processed Data")
    st.dataframe(df)

    # 📌 Summary
    st.subheader("📌 Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("Total Claims", len(df))
    col2.metric("High Risk", (df["Risk"] == "High Risk").sum())
    col3.metric("Auto Approvals", (df["Decision"] == "Auto Approve").sum())

    # 📈 Bar Chart
    st.subheader("📈 Risk Distribution (Bar Chart)")
    risk_counts = df["Risk"].value_counts()
    st.bar_chart(risk_counts)

    # 🥧 Pie Chart
    st.subheader("🥧 Risk Share (Pie Chart)")
    fig, ax = plt.subplots()
    risk_counts.plot.pie(autopct="%1.1f%%", ax=ax)
    ax.set_ylabel("")  # remove label
    st.pyplot(fig)

    # 🔍 Filter
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

else:
    st.info("Please upload a CSV file to proceed.")