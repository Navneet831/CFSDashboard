import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION & COMMON FUNCTIONS (Included in each file)
# =============================================================================
FILE_PATH = r"C:\Users\hp\OneDrive\Desktop\Script\OPL\Base data\OPL CFS v2.xlsx"
CRORE_CONVERSION = 10000000

BG_PRIMARY = '#0f172a'
BG_SECONDARY = '#1e293b'
TEXT_PRIMARY = '#f1f5f9'
TEXT_MUTED = '#94a3b8'
BORDER_COLOR = '#334155'
GRADIENT_DEFAULT_START, GRADIENT_DEFAULT_END = '#1e3a8a', '#7c3aed'

st.set_page_config(page_title="Transaction Details", page_icon="📋", layout="wide", initial_sidebar_state="collapsed")

def get_base_styles():
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp {{ background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY}; }}
        * {{ font-family: 'Inter', sans-serif; }}
        .main-header {{ background: linear-gradient(135deg, {GRADIENT_DEFAULT_START} 0%, {GRADIENT_DEFAULT_END} 100%); padding: 1.5rem; border-radius: 16px; margin-bottom: 1.5rem; }}
        .main-header h1 {{ color: {TEXT_PRIMARY}; font-size: 1.75rem; font-weight: 700; margin: 0; }}
        .table-container {{ background: {BG_SECONDARY}; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem; border: 1px solid {BORDER_COLOR}; }}
        .copyright {{ text-align: center; color: {TEXT_MUTED}; font-size: 0.75rem; margin-top: 2rem; padding-top: 1rem; border-top: 1px solid {BORDER_COLOR}; }}
    </style>
    """

@st.cache_data(ttl=300)
def load_excel_data():
    try:
        xls = pd.ExcelFile(FILE_PATH)
        bank_data = {}
        bank_name_mapping = {'sbi': 'SBI', 'icici': 'ICICI', 'hdfc': 'HDFC', 'federal': 'Federal', 'axis': 'Axis', 'yes': 'Yes', 'yes bank': 'Yes'}
        for sheet in xls.sheet_names:
            df, sheet_lower = pd.read_excel(xls, sheet_name=sheet), sheet.lower()
            if 'forecast' not in sheet_lower:
                bank_name = next((val for key, val in bank_name_mapping.items() if key in sheet_lower), None)
                if bank_name:
                    try:
                        bank_data[bank_name] = pd.DataFrame({'Value_Date': pd.to_datetime(df.iloc[:, 2], errors='coerce'), 'Net_Flow': pd.to_numeric(df.iloc[:, 8], errors='coerce'), 'Category': df.iloc[:, 11].fillna('Unknown'), 'Remarks': df.iloc[:, 12].fillna('') if len(df.columns) > 12 else '', 'Bank': bank_name}).dropna(subset=['Value_Date', 'Net_Flow'])
                    except Exception: pass
        return bank_data
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return {}

def consolidate_bank_data(bank_data, start_date, end_date):
    if not bank_data: return pd.DataFrame()
    return pd.concat(list(bank_data.values())).query("@start_date <= Value_Date <= @end_date")

# =============================================================================
# MAIN APP LOGIC
# =============================================================================
def app():
    st.markdown(get_base_styles(), unsafe_allow_html=True)
    st.markdown("<div class='main-header'><h1>📋 Transaction Details</h1></div>", unsafe_allow_html=True)

    bank_data = load_excel_data()
    if not bank_data: return

    all_dates = [d for df in bank_data.values() for d in df['Value_Date'].dropna()]
    if not all_dates:
        st.error("No valid dates found in data.")
        return

    min_date, max_date = min(all_dates).date(), max(all_dates).date()
    c1, c2 = st.columns(2)
    start_date_dt = c1.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date, key="td_from_date")
    end_date_dt = c2.date_input("To Date", value=max_date, min_value=start_date_dt, max_value=max_date, key="td_to_date")

    consolidated_data = consolidate_bank_data(bank_data, pd.Timestamp(start_date_dt), pd.Timestamp(end_date_dt))
    
    if not consolidated_data.empty:
        st.markdown('<div class="table-container">', unsafe_allow_html=True)
        transactions = consolidated_data[['Value_Date', 'Bank', 'Category', 'Net_Flow', 'Remarks']].copy()
        transactions['Net_Flow (Cr)'] = (transactions['Net_Flow'] / CRORE_CONVERSION).round(2)
        transactions['Value_Date'] = transactions['Value_Date'].dt.strftime('%Y-%m-%d')
        st.dataframe(transactions[['Value_Date', 'Bank', 'Category', 'Net_Flow (Cr)', 'Remarks']], use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("📭 No transactions found for the selected date range.")

    st.markdown(f"""<div class="copyright">© {datetime.now().year} Cash Flow Analytics</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    app()