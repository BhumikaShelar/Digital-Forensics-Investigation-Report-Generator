import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import hashlib
import io
import base64

import importlib
import database
importlib.reload(database)
from database import (
    init_db, verify_user, add_user, get_all_cases, get_case_by_id, add_case,
    update_case_status, update_case_details, delete_case, get_evidence_by_case, get_all_evidence, add_evidence,
    get_findings_by_case, get_all_findings, add_finding, log_action, get_audit_logs,
    update_user_last_module, get_user_last_module
)
from pdf_generator import generate_pdf_report
from sample_data import seed_sample_data

# Initialize Streamlit Page Config
st.set_page_config(
    page_title="Digital Forensic Investigation System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Database & Sample Data
init_db()
seed_sample_data()

# Inject Custom Cyber / Forensic UI Styling (Dark Slate & Glassmorphism Theme)
st.markdown("""
<style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0b1120;
        color: #f1f5f9;
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #1e293b;
    }

    /* Custom Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #38bdf8;
    }
    .metric-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-value {
        color: #38bdf8;
        font-size: 2rem;
        font-weight: 700;
        margin-top: 5px;
    }

    /* Forensic Header Banner */
    .forensic-header {
        background: linear-gradient(90deg, #1e293b 0%, #0f172a 100%);
        border-bottom: 2px solid #0284c7;
        padding: 16px 24px;
        border-radius: 10px;
        margin-bottom: 25px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .forensic-title {
        color: #f8fafc;
        font-size: 1.5rem;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .forensic-sub {
        color: #38bdf8;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
    }

    /* Status Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        display: inline-block;
    }
    .badge-critical { background-color: rgba(220, 38, 38, 0.2); color: #ef4444; border: 1px solid #ef4444; }
    .badge-high { background-color: rgba(234, 88, 12, 0.2); color: #f97316; border: 1px solid #f97316; }
    .badge-medium { background-color: rgba(217, 119, 6, 0.2); color: #f59e0b; border: 1px solid #f59e0b; }
    .badge-low { background-color: rgba(37, 99, 235, 0.2); color: #60a5fa; border: 1px solid #60a5fa; }
    .badge-info { background-color: rgba(22, 163, 74, 0.2); color: #4ade80; border: 1px solid #4ade80; }

    /* Code Monospace Box */
    .hash-code {
        font-family: 'Fira Code', 'Courier New', monospace;
        background-color: #020617;
        color: #38bdf8;
        padding: 4px 8px;
        border-radius: 4px;
        border: 1px solid #1e293b;
        font-size: 0.8rem;
        word-break: break-all;
    }

    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        border-radius: 6px;
        color: #94a3b8;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0284c7 !important;
        color: #ffffff !important;
    }

    /* Hide top Streamlit header, toolbar, and white band */
    header[data-testid="stHeader"], [data-testid="stHeader"], #MainMenu, footer, .stAppHeader {
        display: none !important;
        visibility: hidden !important;
        height: 0px !important;
        margin: 0px !important;
        padding: 0px !important;
    }

    /* Reset Download Button Outer Container Wrappers (Remove double box outline) */
    .stDownloadButton, 
    div[data-testid="stDownloadButton"] {
        border: none !important;
        background: transparent !important;
        background-color: transparent !important;
        padding: 0 !important;
        margin: 0 !important;
        box-shadow: none !important;
    }

    /* Single Clean Button Styling for Regular, Submit, and Download Buttons */
    .stButton > button, 
    .stDownloadButton > button, 
    .stDownloadButton > a,
    div[data-testid="stFormSubmitButton"] > button, 
    div[data-testid="stDownloadButton"] > button,
    div[data-testid="stDownloadButton"] > a,
    button[data-testid="stBaseButton-secondary"],
    button[data-testid="stBaseButton-primary"],
    a[data-testid="stBaseButton-secondary"],
    a[data-testid="stBaseButton-primary"],
    button[kind="primary"] {
        background-color: #0f172a !important;
        background: #0f172a !important;
        color: #ffffff !important;
        border: 1px solid #38bdf8 !important;
        border-radius: 8px !important;
        font-weight: 700 !important;
        padding: 0.6rem 1.2rem !important;
        transition: all 0.2s ease-in-out !important;
        text-decoration: none !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }
    
    /* Force all inner text, paragraph, span, div elements inside download buttons to solid bright white */
    .stDownloadButton *, 
    div[data-testid="stDownloadButton"] *,
    button[data-testid="stBaseButton-secondary"] *,
    button[data-testid="stBaseButton-primary"] * {
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        font-weight: 700 !important;
        opacity: 1 !important;
        background-color: transparent !important;
    }

    .stButton > button:hover, 
    .stDownloadButton > button:hover, 
    .stDownloadButton > a:hover,
    div[data-testid="stFormSubmitButton"] > button:hover, 
    div[data-testid="stDownloadButton"] > button:hover,
    div[data-testid="stDownloadButton"] > a:hover,
    button[data-testid="stBaseButton-secondary"]:hover,
    button[data-testid="stBaseButton-primary"]:hover,
    a[data-testid="stBaseButton-secondary"]:hover,
    a[data-testid="stBaseButton-primary"]:hover,
    button[kind="primary"]:hover {
        background-color: #0284c7 !important;
        background: #0284c7 !important;
        color: #ffffff !important;
        border-color: #38bdf8 !important;
        box-shadow: 0 4px 14px rgba(2, 132, 199, 0.4) !important;
    }
    .stButton > button:active, .stDownloadButton > button:active, div[data-testid="stFormSubmitButton"] > button:active {
        background-color: #0369a1 !important;
        background: #0369a1 !important;
    }

    /* Form Labels High Contrast */
    label, [data-testid="stWidgetLabel"], .stWidgetLabel label, p[data-testid="stWidgetLabel"] {
        color: #e2e8f0 !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
    }

    /* Input Fields (Text input, Textarea, Selectbox) High Contrast Styling */
    .stTextInput input, .stTextArea textarea, div[data-baseweb="select"] > div, div[data-baseweb="input"] {
        background-color: #0f172a !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }

    /* Text inside textarea & text input */
    .stTextInput input, .stTextArea textarea {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        background-color: #0f172a !important;
    }

    /* Input Focus state */
    .stTextInput input:focus, .stTextArea textarea:focus, div[data-baseweb="select"]:focus-within {
        border-color: #38bdf8 !important;
        box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.25) !important;
    }

    /* Dropdown Menus & Popover Styling */
    div[data-baseweb="popover"], div[data-baseweb="menu"], ul[role="listbox"] {
        background-color: #0f172a !important;
        border: 1px solid #334155 !important;
    }
    li[role="option"] {
        color: #f8fafc !important;
        background-color: #0f172a !important;
    }
    li[role="option"]:hover, li[aria-selected="true"] {
        background-color: #1e293b !important;
        color: #38bdf8 !important;
    }

    /* Sidebar Radio Navigation Options High Contrast */
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div[role="radiogroup"] label span,
    [data-testid="stSidebar"] label p {
        color: #f8fafc !important;
        -webkit-text-fill-color: #f8fafc !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }
    
    /* Selected sidebar item accent */
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] span,
    [data-testid="stSidebar"] div[role="radiogroup"] [aria-checked="true"] p {
        color: #38bdf8 !important;
        -webkit-text-fill-color: #38bdf8 !important;
        font-weight: 700 !important;
    }
</style>
""", unsafe_allow_html=True)

# Session State Setup
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "user_info" not in st.session_state:
    st.session_state.user_info = None

# Helper Functions
def login_user(username, password):
    user = verify_user(username, password)
    if user:
        st.session_state.authenticated = True
        st.session_state.user_info = dict(user)
        last_mod = get_user_last_module(user["username"])
        st.session_state.active_module = last_mod
        log_action(user["username"], "Login", f"User logged into system (resuming at '{last_mod}')")
        return True
    return False

def logout_user():
    if st.session_state.user_info:
        log_action(st.session_state.user_info["username"], "Logout", "User logged out")
    st.session_state.authenticated = False
    st.session_state.user_info = None

def compute_file_hash(file_bytes):
    sha256 = hashlib.sha256(file_bytes).hexdigest()
    md5 = hashlib.md5(file_bytes).hexdigest()
    return sha256, md5


# ==========================================
# 🔐 AUTHENTICATION SCREEN (Sign In & Sign Up)
# ==========================================
if not st.session_state.authenticated:
    st.markdown("<br/><br/>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="font-size: 3rem;">🛡️</div>
            <h1 style="color: #f8fafc; font-size: 1.8rem; font-weight: 800; margin-bottom: 5px;">DIGITAL FORENSIC INVESTIGATION SYSTEM</h1>
            <p style="color: #38bdf8; font-size: 0.9rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.1em;">
                Secure Evidence Repository & Automated Report Generator
            </p>
        </div>
        """, unsafe_allow_html=True)

        auth_tab1, auth_tab2 = st.tabs(["🔑 Sign In", "📝 User Sign Up"])

        with auth_tab1:
            with st.form("login_form"):
                st.subheader("🔑 Investigator & Admin Sign In")
                username_input = st.text_input("Investigator Username", placeholder="Enter your username", value="admin")
                password_input = st.text_input("Password", type="password", placeholder="Enter your password", value="admin123")
                submit_login = st.form_submit_button("Sign In & Enter System", use_container_width=True)

                if submit_login:
                    if not username_input or not password_input:
                        st.error("Please enter both username and password.")
                    elif login_user(username_input, password_input):
                        st.success("Authentication Successful! Redirecting to Dashboard...")
                        st.rerun()
                    else:
                        st.error("Invalid credentials. If you are a new user, please Sign Up first. Admin can sign in directly with admin / admin123.")



        with auth_tab2:
            with st.form("signup_form"):
                st.subheader("📝 User Registration / Sign Up")
                new_fullname = st.text_input("Full Name", placeholder="e.g. Detective John Doe")
                new_username = st.text_input("Choose Username", placeholder="e.g. johndoe")
                new_password = st.text_input("Choose Password", type="password", placeholder="At least 4 characters")
                confirm_password = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
                new_role = st.selectbox("Investigator Role", [
                    "Digital Forensic Analyst",
                    "Incident Responder",
                    "Evidence Auditor",
                    "Cybersecurity Analyst"
                ])

                submit_signup = st.form_submit_button("Create Account & Register", use_container_width=True)

                if submit_signup:
                    if not new_fullname or not new_username or not new_password:
                        st.error("All fields (Full Name, Username, Password) are required!")
                    elif len(new_password) < 4:
                        st.error("Password must be at least 4 characters long.")
                    elif new_password != confirm_password:
                        st.error("Passwords do not match! Please check and try again.")
                    elif new_username.lower() == "admin":
                        st.error("Username 'admin' is reserved. Admin can directly Sign In without signing up.")
                    else:
                        success = add_user(new_username.strip(), new_password, new_fullname.strip(), new_role)
                        if success:
                            log_action(new_username.strip(), "User Sign Up", f"New user registered: {new_fullname.strip()} ({new_role})")
                            st.success(f"🎉 Account successfully created for '{new_username}'! Please switch to the 'Sign In' tab to log in.")
                        else:
                            st.error(f"Username '{new_username}' already exists. Please choose a different username or Sign In.")

    st.stop()


# ==========================================
# 🧭 SIDEBAR NAVIGATION & SYSTEM HEADER
# ==========================================
with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0; text-align: center; border-bottom: 1px solid #1e293b; margin-bottom: 15px;">
        <div style="font-size: 2.2rem;">🛡️</div>
        <div style="font-size: 1.1rem; font-weight: 800; color: #f8fafc;">DF-REPORT ENGINE</div>
        <div style="font-size: 0.75rem; color: #38bdf8; font-weight: 600;">TOPIC 7 • FORENSIC MODEL</div>
    </div>
    """, unsafe_allow_html=True)

    user_info = st.session_state.get("user_info") or {}
    user_name = user_info.get("full_name", "Investigator")
    user_role = user_info.get("role", "Analyst")
    st.markdown(f"👤 **{user_name}**  \n<small style='color: #94a3b8;'>Role: {user_role}</small>", unsafe_allow_html=True)
    st.markdown("---")

    menu_options = [
        "📊 Dashboard",
        "📁 Case Management",
        "💻 Evidence Tracker",
        "🔍 Forensic Findings",
        "📄 Report Generator",
        "📜 Search & Report History",
        "🛡️ Hash Integrity Verifier",
        "📋 Audit Logs"
    ]

    username = user_info.get("username", "")
    saved_module = st.session_state.get("active_module") or get_user_last_module(username)
    if saved_module not in menu_options:
        saved_module = "📊 Dashboard"
    
    default_idx = menu_options.index(saved_module)

    menu_option = st.radio(
        "NAVIGATION MENU",
        menu_options,
        index=default_idx
    )

    # Automatically save user's progress & last visited module
    if menu_option != st.session_state.get("active_module"):
        st.session_state.active_module = menu_option
        if username:
            update_user_last_module(username, menu_option)

    st.markdown("---")
    if st.button("🚪 Logout Session", use_container_width=True):
        logout_user()
        st.rerun()


# ==========================================
# 📊 MODULE 1: DASHBOARD
# ==========================================
if menu_option == "📊 Dashboard":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">📊 INVESTIGATION COMMAND DASHBOARD</div>
            <div class="forensic-sub">Real-Time Case Metrics, Evidence Status & High-Priority Artifacts</div>
        </div>
        <div style="text-align: right;">
            <span class="badge badge-info">System Operational</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cases = get_all_cases()
    evidence_list = get_all_evidence()
    findings_list = get_all_findings()

    # Metric Row
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Total Cases</div>
            <div class="metric-value">{len(cases)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Evidence Items</div>
            <div class="metric-value" style="color: #38bdf8;">{len(evidence_list)}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        completed_cases = len([c for c in cases if c['status'] == 'Completed'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Completed Reports</div>
            <div class="metric-value" style="color: #4ade80;">{completed_cases}</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        active_cases = len([c for c in cases if c['status'] != 'Completed'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Active Examinations</div>
            <div class="metric-value" style="color: #f59e0b;">{active_cases}</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        crit_findings = len([f for f in findings_list if f['severity'] == 'Critical'])
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Critical Findings</div>
            <div class="metric-value" style="color: #ef4444;">{crit_findings}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br/>", unsafe_allow_html=True)

    # Interactive Plotly Charts
    g1, g2 = st.columns(2)

    with g1:
        st.subheader("📈 Case Status Distribution")
        if cases:
            df_cases = pd.DataFrame(cases)
            status_counts = df_cases['status'].value_counts().reset_index()
            status_counts.columns = ['Status', 'Count']
            fig_status = px.pie(
                status_counts,
                names='Status',
                values='Count',
                hole=0.4,
                color_discrete_sequence=['#0284c7', '#16a34a', '#eab308', '#dc2626']
            )
            fig_status.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc'),
                margin=dict(t=20, b=20, l=20, r=20)
            )
            st.plotly_chart(fig_status, use_container_width=True)

    with g2:
        st.subheader("🔥 Findings Breakdown by Severity")
        if findings_list:
            df_find = pd.DataFrame(findings_list)
            sev_counts = df_find['severity'].value_counts().reset_index()
            sev_counts.columns = ['Severity', 'Count']
            color_map = {'Critical': '#dc2626', 'High': '#ea580c', 'Medium': '#d97706', 'Low': '#2563eb', 'Info': '#16a34a'}
            fig_sev = px.bar(
                sev_counts,
                x='Severity',
                y='Count',
                color='Severity',
                color_discrete_map=color_map,
                text='Count'
            )
            fig_sev.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#f8fafc'),
                margin=dict(t=20, b=20, l=20, r=20),
                showlegend=False
            )
            st.plotly_chart(fig_sev, use_container_width=True)

    # Recent Cases Overview Table & Interactive Inspector
    st.subheader("📁 Recent Case Summary & Interactive Inspector")
    if cases:
        df_recent = pd.DataFrame(cases)[['case_id', 'case_name', 'investigator', 'created_date', 'priority', 'status']]
        
        selected_event = st.dataframe(
            df_recent,
            use_container_width=True,
            hide_index=True,
            selection_mode="single-row",
            on_select="rerun",
            key="dash_table_select"
        )

        selected_case_id = None
        selected_rows = selected_event.selection.rows if hasattr(selected_event, "selection") else []
        if selected_rows:
            selected_case_id = df_recent.iloc[selected_rows[0]]['case_id']

        case_options = [f"[{c['case_id']}] {c['case_name']} ({c['status']})" for c in cases]
        default_case_idx = 0
        if selected_case_id:
            for idx, c in enumerate(cases):
                if c['case_id'] == selected_case_id:
                    default_case_idx = idx
                    break

        st.markdown("💡 **Click any row in the table above or select a case below to inspect and edit details:**")
        chosen_case_str = st.selectbox(
            "🔍 Selected Case File:",
            case_options,
            index=default_case_idx,
            key="dash_case_selector"
        )
        
        target_case_id = chosen_case_str.split("]")[0].replace("[", "").strip()
        target_case = get_case_by_id(target_case_id)

        if target_case:
            with st.expander(f"📝 **INSPECT & EDIT CASE DETAILS: [{target_case['case_id']}] {target_case['case_name']}**", expanded=True):
                with st.form(key=f"edit_case_form_{target_case['case_id']}"):
                    st.markdown("#### ✏️ Update Case Information & Add Details")
                    e_col1, e_col2 = st.columns(2)
                    with e_col1:
                        edit_name = st.text_input("Case Title / Name", value=target_case['case_name'])
                        edit_investigator = st.text_input("Lead Investigator", value=target_case['investigator'])
                        edit_client = st.text_input("Target Client / Department", value=target_case.get('client_org', 'Internal Incident Response'))
                    with e_col2:
                        status_opts = ["In Progress", "Under Examination", "Pending Review", "Completed"]
                        edit_status = st.selectbox("Case Status", status_opts, index=status_opts.index(target_case['status']) if target_case['status'] in status_opts else 0)
                        priority_opts = ["Critical", "High", "Medium", "Low"]
                        edit_priority = st.selectbox("Priority Level", priority_opts, index=priority_opts.index(target_case['priority']) if target_case['priority'] in priority_opts else 0)
                    
                    edit_desc = st.text_area("Investigation Description & Scope", value=target_case.get('description', ''), height=120)
                    
                    save_case_btn = st.form_submit_button("💾 Save Case Updates", use_container_width=True)
                    if save_case_btn:
                        update_case_details(target_case['case_id'], edit_name, edit_investigator, edit_status, edit_priority, edit_desc, edit_client)
                        log_action(st.session_state.user_info["username"], "Edit Case", f"Updated details for Case {target_case['case_id']}")
                        st.success(f"✅ Case '{target_case['case_id']}' details updated successfully!")
                        st.rerun()

                # Linked Evidence and Findings Summary
                ev_linked = get_evidence_by_case(target_case['case_id'])
                fin_linked = get_findings_by_case(target_case['case_id'])
                st.markdown(f"📦 **Linked Evidence Items:** `{len(ev_linked)} item(s)` | 🔍 **Linked Findings:** `{len(fin_linked)} finding(s)`")
                if ev_linked:
                    st.dataframe(pd.DataFrame(ev_linked)[['evidence_id', 'evidence_type', 'source_device', 'file_hash_sha256']], use_container_width=True, hide_index=True)


# ==========================================
# 📁 MODULE 2: CASE MANAGEMENT
# ==========================================
elif menu_option == "📁 Case Management":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">📁 CASE MANAGEMENT MODULE</div>
            <div class="forensic-sub">Register New Digital Forensic Investigation Files & Update Case Status</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["➕ Create New Case", "📋 Active Case Registry"])

    with tab1:
        with st.form("create_case_form"):
            c1, c2 = st.columns(2)
            with c1:
                auto_case_id = f"DF-2026-00{len(get_all_cases()) + 1:02d}"
                case_id = st.text_input("Case ID", value=auto_case_id)
                case_name = st.text_input("Case Title / Name", placeholder="e.g. Workstation Data Leak Investigation")
                investigator = st.text_input("Lead Investigator Name", value=st.session_state.user_info.get("full_name", ""))
            with c2:
                client_org = st.text_input("Target Client / Department", value="Internal Incident Response")
                status = st.selectbox("Initial Status", ["In Progress", "Under Examination", "Pending Review", "Completed"])
                priority = st.selectbox("Priority Level", ["Critical", "High", "Medium", "Low"])

            description = st.text_area("Investigation Description & Scope", placeholder="Describe the trigger event, suspect devices, and investigation objectives...")
            submit_case = st.form_submit_button("📁 Register Case File", use_container_width=True)

            if submit_case:
                if not case_id or not case_name:
                    st.error("Case ID and Case Name are required!")
                else:
                    created_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    add_case(case_id, case_name, investigator, created_date, status, priority, description, client_org)
                    log_action(st.session_state.user_info["username"], "Create Case", f"Registered Case {case_id}: {case_name}")
                    st.success(f"Case '{case_id}' successfully created!")
                    st.rerun()

    with tab2:
        cases = get_all_cases()
        if cases:
            for c in cases:
                with st.expander(f"📁 **[{c['case_id']}] {c['case_name']}** — Priority: {c['priority']} | Status: {c['status']}"):
                    with st.form(key=f"m2_edit_case_form_{c['case_id']}"):
                        col_a, col_b = st.columns(2)
                        with col_a:
                            m2_name = st.text_input("Case Title / Name", value=c['case_name'], key=f"m2_n_{c['case_id']}")
                            m2_inv = st.text_input("Lead Investigator", value=c['investigator'], key=f"m2_i_{c['case_id']}")
                            m2_client = st.text_input("Client Org", value=c.get('client_org', 'Internal'), key=f"m2_c_{c['case_id']}")
                        with col_b:
                            status_opts = ["In Progress", "Under Examination", "Pending Review", "Completed"]
                            m2_status = st.selectbox("Update Status", status_opts, index=status_opts.index(c['status']) if c['status'] in status_opts else 0, key=f"m2_s_{c['case_id']}")
                            priority_opts = ["Critical", "High", "Medium", "Low"]
                            m2_priority = st.selectbox("Priority Level", priority_opts, index=priority_opts.index(c['priority']) if c['priority'] in priority_opts else 0, key=f"m2_p_{c['case_id']}")

                        m2_desc = st.text_area("Scope / Description", value=c.get('description', ''), key=f"m2_d_{c['case_id']}")
                        
                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            m2_save = st.form_submit_button("💾 Save Case Updates", use_container_width=True)
                            if m2_save:
                                update_case_details(c['case_id'], m2_name, m2_inv, m2_status, m2_priority, m2_desc, m2_client)
                                log_action(st.session_state.user_info["username"], "Edit Case", f"Updated details for Case {c['case_id']}")
                                st.success(f"Case '{c['case_id']}' updated successfully!")
                                st.rerun()
                    
                    st.markdown("<br/>", unsafe_allow_html=True)
                    if st.button("🗑️ Delete Case File", key=f"m2_btn_del_{c['case_id']}", type="secondary", use_container_width=True):
                        delete_case(c['case_id'])
                        log_action(st.session_state.user_info["username"], "Delete Case", f"Deleted Case {c['case_id']}: {c['case_name']}")
                        st.success(f"Case '{c['case_id']}' deleted.")
                        st.rerun()


# ==========================================
# 💻 MODULE 3: EVIDENCE TRACKER
# ==========================================
elif menu_option == "💻 Evidence Tracker":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">💻 EVIDENCE MANAGEMENT & INTEGRITY TRACKER</div>
            <div class="forensic-sub">Log Hardware & Digital Evidence with Cryptographic SHA-256 Hashing</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    tab_ev1, tab_ev2 = st.tabs(["➕ Add Evidence Item", "📦 Evidence Vault Inventory"])

    cases = get_all_cases()
    case_dict = {f"[{c['case_id']}] {c['case_name']}": c['case_id'] for c in cases}

    with tab_ev1:
        if not cases:
            st.warning("Please create at least one Case in Case Management before adding evidence!")
        else:
            with st.form("add_evidence_form"):
                e_col1, e_col2 = st.columns(2)
                with e_col1:
                    selected_case_label = st.selectbox("Select Target Case File", list(case_dict.keys()))
                    case_id_selected = case_dict[selected_case_label]
                    
                    auto_ev_id = f"E-2026-{len(get_all_evidence()) + 1:03d}A"
                    evidence_id = st.text_input("Evidence ID", value=auto_ev_id)
                    evidence_type = st.selectbox("Evidence Media Type", [
                        "Hard Drive Clone (.E01 / .DD)",
                        "Memory Dump (.raw / .vmem)",
                        "Removable Media (USB / SD Card)",
                        "Mobile Device Backup (iOS / Android)",
                        "Network Packet Capture (.pcap)",
                        "System Server Access Logs (.log)",
                        "Optical Media (CD / DVD)"
                    ])
                    source_device = st.text_input("Source Device / System Identifier", placeholder="e.g. Dell XPS Workstation WS-DEPT-88")
                
                with e_col2:
                    serial_number = st.text_input("Device Serial / Asset Number", placeholder="e.g. SN-8891-XK2")
                    storage_loc = st.text_input("Storage Vault Location", value="Secure Evidence Vault #3, Bin A1")
                    custody = st.text_area("Chain of Custody History", value=f"Seized by {st.session_state.user_info.get('full_name', 'Investigator')} on {datetime.now().strftime('%Y-%m-%d')} -> Sealed in anti-static evidence bag.")

                st.markdown("### 🔐 Cryptographic Hashing Verification")
                st.info("💡 You can upload an actual sample file below (or use the test file above) to **automatically compute** its live SHA-256 and MD5 hash.")

                uploaded_file = st.file_uploader("Upload Evidence File for Auto-Hashing (Optional)", type=None)
                
                calc_sha256 = ""
                calc_md5 = ""

                if uploaded_file is not None:
                    file_bytes = uploaded_file.read()
                    calc_sha256, calc_md5 = compute_file_hash(file_bytes)
                    st.success(f"✅ Live Hash Calculated for '{uploaded_file.name}':")
                    st.markdown(f"**SHA-256:** `<span class='hash-code'>{calc_sha256}</span>`", unsafe_allow_html=True)
                    st.markdown(f"**MD5:** `<span class='hash-code'>{calc_md5}</span>`", unsafe_allow_html=True)

                h_c1, h_c2 = st.columns(2)
                with h_c1:
                    sha256_hash = st.text_input("SHA-256 Hash", value=calc_sha256 if calc_sha256 else "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
                with h_c2:
                    md5_hash = st.text_input("MD5 Hash", value=calc_md5 if calc_md5 else "d41d8cd98f00b204e9800998ecf8427e")

                ev_desc = st.text_area("Evidence Item Description & Notes", placeholder="Detail the physical condition, ports, sealed status, acquisition method...")

                submit_ev = st.form_submit_button("📦 Log Evidence Item", use_container_width=True)

                if submit_ev:
                    if not evidence_id or not source_device:
                        st.error("Evidence ID and Source Device are required!")
                    else:
                        coll_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        add_evidence(
                            evidence_id, case_id_selected, evidence_type, ev_desc,
                            source_device, serial_number, coll_date, sha256_hash,
                            md5_hash, storage_loc, custody
                        )
                        log_action(st.session_state.user_info["username"], "Add Evidence", f"Logged Evidence {evidence_id} to Case {case_id_selected}")
                        st.success(f"Evidence '{evidence_id}' logged successfully!")
                        st.rerun()

    with tab_ev2:
        all_ev = get_all_evidence()
        if all_ev:
            df_ev = pd.DataFrame(all_ev)
            st.dataframe(df_ev[['evidence_id', 'case_id', 'evidence_type', 'source_device', 'collection_date', 'file_hash_sha256', 'storage_location']], use_container_width=True, hide_index=True)
        else:
            st.info("No evidence items logged yet.")


# ==========================================
# 🔍 MODULE 4: FORENSIC FINDINGS
# ==========================================
elif menu_option == "🔍 Forensic Findings":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">🔍 FORENSIC FINDINGS & ARTIFACT LOG ENGINE</div>
            <div class="forensic-sub">Document Suspicious Files, Registry Keys, Volatile Memory & Browser History</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cases = get_all_cases()
    case_dict = {f"[{c['case_id']}] {c['case_name']}": c['case_id'] for c in cases}

    if not cases:
        st.warning("Please create a Case first before adding findings!")
    else:
        # Quick fill button for testing
        c_fill1, c_fill2 = st.columns([3, 1])
        with c_fill2:
            if st.button("⚡ Auto-Fill Sample Data", use_container_width=True, key="btn_autofill_finding"):
                st.session_state["f_name_val"] = "Exfiltrated_Financial_Records_2026.zip"
                st.session_state["f_path_val"] = r"C:\Users\Suspect\AppData\Local\Temp\Exfiltrated_Financial_Records_2026.zip"
                st.session_state["f_hash_val"] = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
                st.session_state["f_desc_val"] = "Encrypted ZIP archive carved from unallocated cluster #48192 using file carving tool. Contains sensitive corporate accounting spreadsheets and database dumps."
                st.session_state["f_notes_val"] = "File timestamp correlates with unauthorized USB insertion event logged in Windows System Event Log #2004."
                st.rerun()

        with st.form("add_finding_form"):
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                selected_case_label = st.selectbox("Select Target Case File", list(case_dict.keys()))
                case_id_selected = case_dict[selected_case_label]
                
                category = st.selectbox("Artifact Category", [
                    "Files Found / Carved Files",
                    "Suspicious Artifacts / Malware Payload",
                    "Device Information & USB Logs",
                    "Browser Information & Web History",
                    "Hash Values & Signatures",
                    "Network Connection & Firewall Logs",
                    "System Registry Entries",
                    "Volatile Memory / Process Injection"
                ])
                artifact_name = st.text_input("Artifact Name", value=st.session_state.get("f_name_val", ""), placeholder="e.g. Encrypted Archive 'confidential.7z'")
                severity = st.selectbox("Severity Level", ["Critical", "High", "Medium", "Low", "Info"])

            with f_col2:
                file_path_location = st.text_input("Artifact Path / Location", value=st.session_state.get("f_path_val", ""), placeholder=r"e.g. C:\Users\suspect\AppData\Local\Temp\~tmp_arc.tmp")
                hash_value = st.text_input("Artifact Hash / Signature (SHA-256 or MD5)", value=st.session_state.get("f_hash_val", ""), placeholder="e.g. e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

            f_desc = st.text_area("Detailed Finding Description", value=st.session_state.get("f_desc_val", ""), placeholder="Explain what the artifact contains, timestamp, deleted state, carving method...")
            notes = st.text_area("Investigator Observations & Technical Notes", value=st.session_state.get("f_notes_val", ""), placeholder="Detailed analysis notes, relation to suspect activity, malware behavior...")

            submit_finding = st.form_submit_button("🔍 Record Forensic Finding", use_container_width=True)

            if submit_finding:
                if not artifact_name or not f_desc:
                    st.error("Artifact Name and Description are required!")
                else:
                    add_finding(
                        case_id_selected, category, artifact_name, f_desc,
                        severity, file_path_location, hash_value, notes
                    )
                    log_action(st.session_state.user_info["username"], "Add Finding", f"Recorded finding '{artifact_name}' for Case {case_id_selected}")
                    st.success(f"Forensic finding '{artifact_name}' added successfully!")
                    st.rerun()

    st.markdown("---")
    st.subheader("📋 Recorded Findings Breakdown")
    all_findings = get_all_findings()
    if all_findings:
        for find in all_findings:
            sev_class = f"badge badge-{find['severity'].lower()}"
            with st.expander(f"🔍 [{find['case_id']}] **{find['artifact_name']}** ({find['category']})"):
                st.markdown(f"""
                **Severity:** <span class="{sev_class}">{find['severity']}</span> &nbsp;&nbsp;|&nbsp;&nbsp; **Recorded:** {find['timestamp']}  
                **Path / System Location:** `<span class="hash-code">{find.get('file_path_location', 'N/A')}</span>`  
                **Hash:** `<span class="hash-code">{find.get('hash_value', 'N/A')}</span>`  
                
                **Description:**  
                {find['description']}  

                **Investigator Notes:**  
                _{find.get('investigator_notes', 'None')}_
                """, unsafe_allow_html=True)


# ==========================================
# 📄 MODULE 5: REPORT GENERATOR
# ==========================================
elif menu_option == "📄 Report Generator":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">📄 AUTOMATED REPORT GENERATION ENGINE</div>
            <div class="forensic-sub">Review Findings, Customize Executive Summary, and Export Publication-Grade PDF</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cases = get_all_cases()
    if not cases:
        st.warning("No cases available. Please create a case file first.")
    else:
        case_options = {f"[{c['case_id']}] {c['case_name']}": c['case_id'] for c in cases}
        selected_case_label = st.selectbox("Select Case to Generate Report For", list(case_options.keys()))
        selected_case_id = case_options[selected_case_label]

        case_obj = get_case_by_id(selected_case_id)
        evidence_objs = get_evidence_by_case(selected_case_id)
        findings_objs = get_findings_by_case(selected_case_id)

        st.markdown("---")
        c_left, c_right = st.columns([1, 1])

        with c_left:
            st.subheader("📝 Customize Report Narrative")
            custom_summary = st.text_area("Executive Summary", value=case_obj.get("description", ""), height=120)
            custom_methodology = st.text_area("Examination Methodology & Tools Used", value="Forensic processing was executed in an isolated laboratory environment using write-blocking hardware (Tableau T8u) and NIST-certified forensic software (Autopsy Forensic Browser, FTK Imager v4.7, Volatility 3, and Python Hashlib Integrity Verification Suite). All disk images were verified against original acquisition cryptographic hashes prior to analysis.", height=120)
            custom_conclusion = st.text_area("Investigator Conclusion & Recommendations", value="Based on the forensic evidence collected and analyzed, the artifacts confirm unauthorized system activity during the timeframe under review. Immediate containment measures, credential resets, and enhanced endpoint monitoring are strongly recommended.", height=120)

            if st.button("🚀 Generate PDF Report", use_container_width=True, type="primary"):
                pdf_bytes = generate_pdf_report(
                    case_obj, evidence_objs, findings_objs,
                    custom_summary, custom_conclusion, custom_methodology
                )
                st.session_state[f"pdf_bytes_{selected_case_id}"] = pdf_bytes
                
                # Save copy to local reports directory
                reports_dir = os.path.join(os.path.dirname(__file__), "reports")
                os.makedirs(reports_dir, exist_ok=True)
                pdf_filename = f"Digital_Forensic_Report_{selected_case_id.replace('-', '_')}.pdf"
                pdf_file_path = os.path.join(reports_dir, pdf_filename)
                with open(pdf_file_path, "wb") as f:
                    f.write(pdf_bytes)
                st.session_state[f"pdf_filepath_{selected_case_id}"] = pdf_file_path

                log_action(st.session_state.user_info["username"], "Generate PDF Report", f"Generated report for Case {selected_case_id}")
                st.success(f"🎉 Official Forensic Report PDF compiled & saved successfully!")

            if f"pdf_bytes_{selected_case_id}" in st.session_state:
                pdf_data = st.session_state[f"pdf_bytes_{selected_case_id}"]
                clean_case_id = selected_case_id.replace("-", "_")
                
                st.download_button(
                    label=f"💾 Download Official Forensic Report ({selected_case_id}.pdf)",
                    data=pdf_data,
                    file_name=f"Digital_Forensic_Report_{clean_case_id}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                    key=f"dl_pdf_btn_{selected_case_id}"
                )

                if f"pdf_filepath_{selected_case_id}" in st.session_state:
                    st.info(f"📁 **Saved on Disk:** `{st.session_state[f'pdf_filepath_{selected_case_id}']}`")

        with c_right:
            st.subheader("👁️ Live PDF & Report Data Preview")
            if f"pdf_bytes_{selected_case_id}" in st.session_state:
                pdf_data = st.session_state[f"pdf_bytes_{selected_case_id}"]
                base64_pdf = base64.b64encode(pdf_data).decode('utf-8')
                pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="520" type="application/pdf" style="border: 1px solid #334155; border-radius: 8px;"></iframe>'
                st.markdown(pdf_display, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #0f172a; padding: 20px; border-radius: 10px; border: 1px solid #1e293b;">
                    <h3 style="color: #38bdf8; margin-top: 0;">DIGITAL FORENSIC INVESTIGATION REPORT</h3>
                    <p><b>Case ID:</b> {case_obj['case_id']}<br/>
                    <b>Case Name:</b> {case_obj['case_name']}<br/>
                    <b>Investigator:</b> {case_obj['investigator']}<br/>
                    <b>Date:</b> {case_obj['created_date']}<br/>
                    <b>Status:</b> {case_obj['status']}<br/>
                    <b>Evidence Logged:</b> {len(evidence_objs)} items<br/>
                    <b>Findings Recorded:</b> {len(findings_objs)} items</p>
                    <hr style="border-color: #334155;"/>
                    <h4 style="color: #f8fafc;">Evidence Summary</h4>
                """, unsafe_allow_html=True)
                for ev in evidence_objs:
                    st.markdown(f"- **{ev['evidence_id']}**: {ev['evidence_type']} (`{ev['source_device']}`)")
                
                st.markdown("<h4 style='color: #f8fafc; margin-top: 15px;'>Findings Summary</h4>", unsafe_allow_html=True)
                for f in findings_objs:
                    st.markdown(f"- **[{f['severity']}]** {f['artifact_name']} — _{f['category']}_")
                st.markdown("</div>", unsafe_allow_html=True)


# ==========================================
# 📜 MODULE 6: SEARCH & REPORT HISTORY
# ==========================================
elif menu_option == "📜 Search & Report History":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">📜 SEARCH PREVIOUS CASES & HISTORICAL REPORTS</div>
            <div class="forensic-sub">Filter Cases by Date, Case ID, Investigator, or Priority</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    cases = get_all_cases()
    if cases:
        df_all = pd.DataFrame(cases)

        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            search_query = st.text_input("🔍 Search Query (ID, Title, Investigator)", placeholder="e.g. DF-2026 or Alex")
        with col_s2:
            status_filter = st.multiselect("Filter by Status", df_all['status'].unique(), default=df_all['status'].unique())
        with col_s3:
            priority_filter = st.multiselect("Filter by Priority", df_all['priority'].unique(), default=df_all['priority'].unique())

        filtered_df = df_all[
            (df_all['status'].isin(status_filter)) &
            (df_all['priority'].isin(priority_filter))
        ]

        if search_query:
            q = search_query.lower()
            filtered_df = filtered_df[
                filtered_df['case_id'].str.lower().str.contains(q) |
                filtered_df['case_name'].str.lower().str.contains(q) |
                filtered_df['investigator'].str.lower().str.contains(q)
            ]

        st.markdown(f"**Found {len(filtered_df)} matching case records:**")
        st.dataframe(filtered_df[['case_id', 'case_name', 'investigator', 'created_date', 'status', 'priority', 'client_org']], use_container_width=True, hide_index=True)

        st.markdown("### 📥 Export Case Registry Data")
        ex_col1, ex_col2 = st.columns(2)
        
        # Save local copy on disk as well
        exports_dir = os.path.join(os.path.dirname(__file__), "exports")
        os.makedirs(exports_dir, exist_ok=True)
        
        csv_str = filtered_df.to_csv(index=False)
        csv_path = os.path.join(exports_dir, "forensic_cases_registry.csv")
        with open(csv_path, "w", encoding="utf-8") as f:
            f.write(csv_str)
            
        json_str = filtered_df.to_json(orient="records", indent=2)
        json_path = os.path.join(exports_dir, "forensic_cases_registry.json")
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        with ex_col1:
            st.download_button(
                label="💾 Download Results as CSV",
                data=csv_str.encode('utf-8'),
                file_name="forensic_cases_registry.csv",
                mime="text/csv",
                use_container_width=True,
                key="btn_dl_csv_registry"
            )
            st.caption(f"📁 Local Disk: `{csv_path}`")
            
        with ex_col2:
            st.download_button(
                label="💾 Download Results as JSON",
                data=json_str.encode('utf-8'),
                file_name="forensic_cases_registry.json",
                mime="application/json",
                use_container_width=True,
                key="btn_dl_json_registry"
            )
            st.caption(f"📁 Local Disk: `{json_path}`")


# ==========================================
# 🛡️ MODULE 7: HASH INTEGRITY VERIFIER
# ==========================================
elif menu_option == "🛡️ Hash Integrity Verifier":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">🛡️ LIVE FILE HASHING & INTEGRITY AUDITOR</div>
            <div class="forensic-sub">Verify Physical / Digital Files Against Recorded Evidence SHA-256 Hashes</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("Upload any suspect file or disk image segment to compute cryptographic hashes and audit for tampering:")

    ver_file = st.file_uploader("Upload Target File for Forensic Hashing", type=None, key="verifier_file")
    
    if ver_file:
        bytes_data = ver_file.read()
        sha256_res, md5_res = compute_file_hash(bytes_data)

        st.subheader("🔍 Calculated Cryptographic Fingerprints")
        st.markdown(f"**File Name:** `{ver_file.name}` ({len(bytes_data):,} bytes)")
        st.markdown(f"**SHA-256 Hash:**  \n`<span class='hash-code'>{sha256_res}</span>`", unsafe_allow_html=True)
        st.markdown(f"**MD5 Hash:**  \n`<span class='hash-code'>{md5_res}</span>`", unsafe_allow_html=True)

        st.markdown("---")
        st.subheader("⚖️ Compare Against Recorded Evidence Hash")
        compare_hash = st.text_input("Paste Expected SHA-256 Hash from Evidence Log", placeholder="e.g. e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")

        if compare_hash:
            clean_expected = compare_hash.strip().lower()
            clean_actual = sha256_res.strip().lower()
            if clean_expected == clean_actual:
                st.success("✅ **CRYPTOGRAPHIC MATCH VERIFIED!**  \nThe file hash perfectly matches the evidence log. No tampering or corruption detected.")
                log_action(st.session_state.user_info["username"], "Hash Integrity Audit", f"Hash MATCH for file {ver_file.name}")
            else:
                st.error("⚠️ **WARNING: HASH MISMATCH DETECTED!**  \nThe calculated hash DOES NOT match the expected evidence hash. Evidence integrity may be compromised.")
                log_action(st.session_state.user_info["username"], "Hash Integrity Audit Failure", f"Hash MISMATCH for file {ver_file.name}")


# ==========================================
# 📋 MODULE 8: AUDIT LOGS
# ==========================================
elif menu_option == "📋 Audit Logs":
    st.markdown("""
    <div class="forensic-header">
        <div>
            <div class="forensic-title">📋 SYSTEM SECURITY & AUDIT TRAIL</div>
            <div class="forensic-sub">Immutable Log of User Actions, Case Access, and Report Generations</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    logs = get_audit_logs()
    if logs:
        df_logs = pd.DataFrame(logs)
        st.dataframe(df_logs[['timestamp', 'user', 'action', 'details']], use_container_width=True, hide_index=True)
    else:
        st.info("No audit log records found.")
