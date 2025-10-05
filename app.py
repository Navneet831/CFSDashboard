import streamlit as st

# =============================================================================
# CORRECTED RELATIVE IMPORTS
# =============================================================================
# The dot (.) tells Python to look for these modules in the same folder
# as the current file (CFS_Main.py). This is the standard for Python packages.
from . import Overview
from . import Variance_Analysis
from . import Trend_Analysis
from . import Bank_Analysis
from . import Transaction_details

# No changes are needed to your existing functions, only the imports.

def main():
    st.title("CFS Dashboard")

    tabs = st.tabs([
        "Overview",
        "Variance Analysis",
        "Trend Analysis",
        "Bank Analysis",
        "Transaction Details",
    ])

    with tabs[0]:
        Overview.app()
    with tabs[1]:
        Variance_Analysis.app()
    with tabs[2]:
        Trend_Analysis.app()
    with tabs[3]:
        Bank_Analysis.app()
    with tabs[4]:
        Transaction_details.app()

def app():
    main()

if __name__ == "__main__":
    main()
