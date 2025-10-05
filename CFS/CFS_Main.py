import streamlit as st

# =============================================================================
# CORRECTED RELATIVE IMPORTS
# =============================================================================
# The dot (.) tells Python to look for these modules in the CURRENT FOLDER
# (the 'CFS' folder). This is the critical fix.
from . import Overview
from . import Variance_Analysis
from . import Trend_Analysis
from . import Bank_Analysis
from . import Transaction_details


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

# This allows the script to be run directly for testing if needed,
# but more importantly, it works correctly when imported by app.py
if __name__ == "__main__":
    main()

