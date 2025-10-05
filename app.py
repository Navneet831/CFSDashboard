import streamlit as st
from datetime import datetime

# =============================================================================
# CORRECTED IMPORTS FOR DEPLOYMENT
# =============================================================================
# This is the correct way to import modules from sub-folders into the main app.
# It does NOT use the dot (.) notation.
from CFS import CFS_Main
from PnL import PnL_Analysis


# =============================================================================
# MAIN APP CONFIGURATION
# =============================================================================
st.set_page_config(
    layout="wide",
    page_title="Finance Review",
    page_icon="⚡",
    initial_sidebar_state="collapsed"
)


# =============================================================================
# GLOBAL STYLING (CSS)
# =============================================================================
# This CSS applies to all dashboards for a consistent look and feel
BG_PRIMARY = '#0f172a'
BG_SECONDARY = '#1e293b'
TEXT_PRIMARY = '#f1f5f9'
TEXT_MUTED = '#94a3b8'
BORDER_COLOR = '#334155'
GRADIENT_START = '#1e3a8a'
GRADIENT_END = '#7c3aed'
ACCENT_SUCCESS = '#10b981'
ACCENT_DANGER = '#ef4444'

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp {{ background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY}; }}
    * {{ font-family: 'Inter', sans-serif; }}

    /* Main Header for the P&L section */
    .main-header {{
        background: linear-gradient(135deg, {GRADIENT_START} 0%, {GRADIENT_END} 100%);
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.2);
    }}
    .main-header h1 {{ color: {TEXT_PRIMARY}; font-size: 1.5rem; font-weight: 700; margin: 0; }}

    /* Metric Card styling used by all dashboards */
    .metric-card {{
        background: {BG_SECONDARY};
        padding: 1.25rem;
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        border: 1px solid {BORDER_COLOR};
        height: 100%;
    }}
    .metric-value {{ font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0; }}
    .metric-value.positive {{ color: {ACCENT_SUCCESS}; }}
    .metric-value.negative {{ color: {DANGER}; }}
    .metric-value.neutral {{ color: {TEXT_PRIMARY}; }}
    .metric-label {{ color: {TEXT_MUTED}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
    .metric-delta {{ font-size: 0.75rem; margin-top: 0.5rem; }}

    /* Container for charts */
    .plot-container {{
        background: {BG_SECONDARY};
        padding: 1.25rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }}

    /* Footer */
    .footer {{
        text-align: center;
        color: {TEXT_MUTED};
        font-size: 0.75rem;
        margin-top: 1rem;
        padding: 0.5rem;
        border-top: 1px solid {BORDER_COLOR};
    }}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# APP LAYOUT & NAVIGATION
# =============================================================================

st.sidebar.title("Navigation")
choice = st.sidebar.radio("Go to", ["CFS", "PnL"], label_visibility="collapsed")


if choice == "CFS":
    CFS_Main.app()

elif choice == "PnL":
    st.markdown("<div class='main-header'><h1>⚡ Financial Dashboard</h1></div>", unsafe_allow_html=True)

    with st.tabs(["P&L Analysis"]):
        PnL_Analysis.app()

# =============================================================================
# FEATURE SUGGESTION BOX
# =============================================================================
with st.sidebar.expander("💡 Suggest a Feature"):
    with st.form("suggestion_form", clear_on_submit=True):
        suggestion = st.text_area("What feature would improve this dashboard?")
        submitted = st.form_submit_button("Submit")
        if submitted and suggestion:
            st.sidebar.success("Thank you for your feedback!")

