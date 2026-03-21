import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import PyPDF2
from sklearn.ensemble import RandomForestClassifier

# --- PAGE CONFIG ---
st.set_page_config(page_title="Smart Claim Analyzer", page_icon="🛡️", layout="wide")

# --- CUSTOM CSS ---
st.markdown("""
<style>
    /* Main background and text colors for dark theme */
    .stApp {
        background-color: #0E1117;
        color: #FFFFFF;
    }
    
    /* Metrics cards */
    div[data-testid="metric-container"] {
        background-color: #1E232F;
        border-radius: 12px;
        padding: 20px;
        border: 1px solid #2D3748;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
    }
    div[data-testid="metric-container"]:hover {
        border-color: #4A5568;
    }
    
    /* Headers */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #12151E;
        border-right: 1px solid #1E232F;
    }
    
    /* File Uploader */
    [data-testid="stFileUploadDropzone"] {
        background-color: #1E232F;
        border: 2px dashed #4A5568;
        border-radius: 12px;
        padding: 30px;
    }
    
    /* Dataframes */
    [data-testid="stDataFrame"] {
        border-radius: 10px;
        overflow: hidden;
        border: 1px solid #2D3748;
    }
    
    /* Success/Warning/Error alerts */
    .stAlert {
        border-radius: 10px;
        border: none;
    }
    
    /* Hide the default radio buttons to make them look cleaner */
    div.row-widget.stRadio > div {
        background-color: transparent;
        padding: 0;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- AUTH SYSTEM ----------------
if "users" not in st.session_state:
    st.session_state.users = {"admin": "admin123"}
    
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.current_user = None

if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style='text-align: center; background-color: #1E232F; padding: 30px; border-radius: 15px; border: 1px solid #2D3748; box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);'>
            <h1 style='color: #FFFFFF; font-size: 2.5rem; margin-bottom: 0px;'>🛡️</h1>
            <h2 style='color: #FFFFFF; margin-top: 10px;'>Smart Claim Analyzer</h2>
            <p style='color: #A0AEC0; margin-bottom: 25px;'>Secure Access Portal</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.markdown("### Welcome Back")
            login_user = st.text_input("Username", key="login_user")
            login_pass = st.text_input("Password", type="password", key="login_pass")
            
            if st.button("Login Securely", use_container_width=True, type="primary"):
                if login_user in st.session_state.users and st.session_state.users[login_user] == login_pass:
                    st.session_state.logged_in = True
                    st.session_state.current_user = login_user
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please try again.")
                    
        with tab2:
            st.markdown("### Create New Account")
            new_user = st.text_input("Choose Username", key="new_user")
            new_pass = st.text_input("Choose Password", type="password", key="new_pass")
            confirm_pass = st.text_input("Confirm Password", type="password", key="confirm_pass")
            
            if st.button("Register Account", use_container_width=True):
                if new_user in st.session_state.users:
                    st.error("Username already exists!")
                elif not new_user or not new_pass:
                    st.warning("Please fill all fields.")
                elif new_pass != confirm_pass:
                    st.error("Passwords do not match!")
                else:
                    st.session_state.users[new_user] = new_pass
                    st.balloons()
                    st.success("Account created successfully! You can now log in using the Login tab.")
    
    st.stop()


# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("## 🛠️ Smart Claim Tool")
    st.markdown("---")
    
    # User Profile Section
    st.markdown(f"👤 **Hey, {st.session_state.current_user}!**")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.rerun()
        
    st.markdown("---")
    page = st.radio("Navigation", ["Dashboard", "Upload Data", "PDF Reader"], label_visibility="collapsed")
    st.markdown("---")
    st.caption("© 2024 Smart Claim Analyzer")
    st.caption("V 2.0 - Premium Edition")

# ---------------- MAIN HEADER ----------------
st.title("🛡️ Smart Claim Analyzer")
st.markdown("<p style='font-size: 1.2rem; color: #A0AEC0;'>AI-powered Claim Risk & Fraud Detection System</p>", unsafe_allow_html=True)
st.divider()

# ---------------- PROCESSING LOGIC (Helper Functions) ----------------
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

# ---------------- UPLOAD DATA ----------------
if page == "Upload Data":
    st.header("📤 Processing Center")
    st.markdown("Upload your claims dataset below to perform AI risk analysis and detect potential fraud anomalies.")
    
    uploaded_file = st.file_uploader("Drop your CSV file here", type=["csv"], help="Limit 200MB per file")
    
    if uploaded_file:
        with st.spinner("Analyzing claims data using Advanced AI..."):
            df = pd.read_csv(uploaded_file)
            
            # Apply Risk Logic
            if not df.empty:
                df["Risk"] = df.apply(calculate_risk, axis=1)
                df["Decision"] = df["Risk"].apply(decision)
                
                # ML Model Simulation
                if "Amount" in df.columns and "Previous_Claims" in df.columns:
                    df["Risk_Label"] = df["Risk"].map({"Low Risk": 0, "Medium Risk": 1, "High Risk": 2})
                    X = df[["Amount", "Previous_Claims"]]
                    y = df["Risk_Label"]
                    
                    model = RandomForestClassifier(random_state=42)
                    model.fit(X, y)
                    df["Predicted_Risk"] = model.predict(X)
                    df["Predicted_Risk"] = df["Predicted_Risk"].map({0: "Low Risk", 1: "Medium Risk", 2: "High Risk"})
                
                st.session_state["data"] = df
                
                st.success("✅ Data processed successfully! 100% records analyzed.")
                
                with st.expander("🔍 View Processed Data", expanded=True):
                    st.dataframe(df, use_container_width=True)
                
                st.info("💡 Head over to the **Dashboard** to view interactive insights.")
            else:
                st.error("Uploaded CSV is empty. Please upload a valid file.")

# ---------------- DASHBOARD ----------------
elif page == "Dashboard":
    st.header("📈 Analytics Dashboard")
    
    if "data" not in st.session_state:
        st.info("👋 Welcome! Please go to **Upload Data** to import your claims dataset first.")
        st.markdown("""
        <div style='text-align: center; padding: 50px; background-color: #1E232F; border-radius: 12px; margin-top: 20px; border: 1px dashed #4A5568;'>
            <h3 style='color: #A0AEC0;'>No Data Available</h3>
            <p style='color: #718096;'>Upload a CSV file to unlock powerful insights and visualizations.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        df = st.session_state["data"]
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        
        total_claims = len(df)
        high_risk = (df["Risk"] == "High Risk").sum()
        auto_approved = (df["Decision"] == "Auto Approve").sum()
        total_amount = df["Amount"].sum() if "Amount" in df.columns else 0
        
        with col1:
            st.metric("Total Claims Processed", f"{total_claims:,}")
        with col2:
            st.metric("High Risk Detected", f"{high_risk:,}", delta=f"{(high_risk/max(total_claims,1))*100:.1f}%", delta_color="inverse")
        with col3:
            st.metric("Auto Approvals", f"{auto_approved:,}", delta=f"{(auto_approved/max(total_claims,1))*100:.1f}%", delta_color="normal")
        with col4:
            st.metric("Total Claim Amount", f"${total_amount:,.2f}" if total_amount > 0 else "N/A")
            
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Alerts
        if high_risk > 0:
            st.error(f"🚨 Immediate Action Required: **{high_risk}** High Risk Claims pending manual review!")
        else:
            st.success("✅ All systems nominal. No high-risk claims detected.")
            
        st.markdown("<br>", unsafe_allow_html=True)
            
        # Charts Section
        st.markdown("### 📊 Distribution Insights")
        tab1, tab2 = st.tabs(["Risk Breakdown", "Data Explorer"])
        
        with tab1:
            chart_col1, chart_col2 = st.columns(2)
            
            with chart_col1:
                st.markdown("#### Risk Level Distribution")
                risk_counts = df["Risk"].value_counts()
                st.bar_chart(risk_counts, color="#FF4B4B")
                
            with chart_col2:
                st.markdown("#### Risk Share Proportion")
                fig, ax = plt.subplots(figsize=(6, 4))
                fig.patch.set_facecolor('#0E1117')
                ax.set_facecolor('#0E1117')
                
                idx = risk_counts.index
                c_map = {"Low Risk": "#00C853", "Medium Risk": "#FFD600", "High Risk": "#FF1744"}
                pie_colors = [c_map.get(x, '#888888') for x in idx]
                
                wedges, texts, autotexts = ax.pie(
                    risk_counts, 
                    labels=risk_counts.index, 
                    autopct="%1.1f%%",
                    colors=pie_colors,
                    textprops={'color': "white", 'fontsize': 10},
                    startangle=90,
                    explode=[0.05]*len(risk_counts)
                )
                
                for autotext in autotexts:
                    autotext.set_color('black')
                    autotext.set_weight('bold')
                    
                ax.axis('equal')
                st.pyplot(fig)
                
        with tab2:
            st.markdown("#### 🔍 Filter & Explore")
            
            filter_col1, filter_col2 = st.columns([1, 3])
            with filter_col1:
                risk_filter = st.selectbox("Select Risk Level", ["All", "Low Risk", "Medium Risk", "High Risk"])
            
            filtered_df = df if risk_filter == "All" else df[df["Risk"] == risk_filter]
            st.dataframe(filtered_df, use_container_width=True)

# ---------------- PDF READER ----------------
elif page == "PDF Reader":
    st.header("📄 Intelligent PDF Claims Reader")
    st.markdown("Upload scanned claim documents or PDF invoices to extract raw text for NLP analysis.")
    
    pdf_file = st.file_uploader("Drop PDF Document", type=["pdf"], help="Supports multi-page PDFs")
    
    if pdf_file:
        with st.spinner("Extracting text contents..."):
            reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            progress_bar = st.progress(0)
            total_pages = len(reader.pages)
            
            for i, page_obj in enumerate(reader.pages):
                extracted = page_obj.extract_text()
                if extracted:
                    text += extracted + "\n\n"
                progress_bar.progress((i + 1) / total_pages)
                
            st.success(f"✅ Successfully extracted text from {total_pages} pages!")
            
            with st.expander("👁️ View Extracted Text", expanded=True):
                st.text_area("Document Context", text, height=400)
                
            col1, col2 = st.columns(2)
            with col1:
                st.info("🧠 **Next Steps**: Feed this text into an LLM to extract **Amount**, **Hospital Name**, and **Patient Details** automatically.", icon="ℹ️")
            with col2:
                st.download_button(
                    label="📥 Download Extracted Text",
                    data=text,
                    file_name="extracted_claim.txt",
                    mime="text/plain",
                    use_container_width=True
                )
