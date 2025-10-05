import streamlit as st
import Overview
import Variance_Analysis
import Trend_Analysis
import Bank_Analysis
import Transaction_details

st.set_page_config(layout="wide", page_title="OPL CFS Dashboard")

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

# ✅ This allows both independent run and import into FR_Main
if __name__ == "__main__":
    main()
