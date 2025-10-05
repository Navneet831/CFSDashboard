import streamlit as st
import pandas as pd
from datetime import datetime, timedelta, date
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION & COMMON FUNCTIONS (Included in each file)
# =============================================================================
FILE_PATH = r"C:\Users\hp\OneDrive\Desktop\Oriana\Cash flow\OPL CFS.xlsx"
CRORE_CONVERSION = 10000000
BANK_LIMITS = {
    'SBI': 69000000,
    'ICICI': 100000000,
    'HDFC': 100000000,
    'Federal': 150000000,
    'Axis': 5000000,
    'Yes': 50000000
}
POSITIVE_BALANCE_BANKS = ['SBI', 'ICICI', 'HDFC', 'Yes']
NEGATIVE_BALANCE_BANKS = ['Federal', 'Axis']

BG_PRIMARY = '#0f172a'
BG_SECONDARY = '#1e293b'
TEXT_PRIMARY = '#f1f5f9'
TEXT_MUTED = '#94a3b8'
BORDER_COLOR = '#334155'
GRADIENT_DEFAULT_START, GRADIENT_DEFAULT_END = '#1e3a8a', '#7c3aed'

st.set_page_config(page_title="Bank Analysis", page_icon="🏦", layout="wide", initial_sidebar_state="collapsed")

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
                        bank_data[bank_name] = pd.DataFrame({'Value_Date': pd.to_datetime(df.iloc[:, 2], errors='coerce'), 'Running_Balance': pd.to_numeric(df.iloc[:, 9], errors='coerce')}).dropna(subset=['Value_Date'])
                    except Exception: pass
        return bank_data
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return {}

def get_balance_on_date(bank_data, bank_name, target_date):
    if bank_name not in bank_data or bank_data[bank_name].empty: return 0
    df_filtered = bank_data[bank_name][bank_data[bank_name]['Value_Date'] <= target_date]
    if df_filtered.empty: return 0
    return df_filtered.sort_values('Value_Date')['Running_Balance'].iloc[-1]

def get_bank_balances(bank_data, as_of_date):
    bank_balances = {}
    for bank, limit in BANK_LIMITS.items():
        balance = get_balance_on_date(bank_data, bank, as_of_date)
        used = -balance if bank in POSITIVE_BALANCE_BANKS else balance
        available = (limit + balance) if bank in POSITIVE_BALANCE_BANKS else (limit - balance)
        utilization = (abs(used) / limit * 100) if limit > 0 else 0
        bank_balances[bank] = {'limit': limit, 'used': used, 'available': available, 'utilization': utilization}
    return bank_balances

# =============================================================================
# MAIN APP LOGIC
# =============================================================================
def app():
    st.markdown(get_base_styles(), unsafe_allow_html=True)
    st.markdown("<div class='main-header'><h1>🏦 Bank Analysis</h1></div>", unsafe_allow_html=True)

    bank_data = load_excel_data()
    if not bank_data: return

    all_dates = [d for df in bank_data.values() for d in df['Value_Date'].dropna()]
    if not all_dates:
        st.error("No valid dates found in data.")
        return

    min_date, max_date = min(all_dates).date(), max(all_dates).date()
    end_date_dt = st.date_input("Select 'As Of' Date", value=max_date, min_value=min_date, max_value=max_date, key="bank_asof_date")
    
    bank_balances = get_bank_balances(bank_data, pd.Timestamp(end_date_dt))

    st.markdown("### Bank-wise Limit Details")
    st.markdown('<div class="table-container">', unsafe_allow_html=True)
    bank_details = [{"Bank": bank, "Limit (Cr)": data['limit']/CRORE_CONVERSION, "Used (Cr)": data['used']/CRORE_CONVERSION, "Available (Cr)": data['available']/CRORE_CONVERSION, "Utilization (%)": f"{data['utilization']:.2f}%"} for bank, data in bank_balances.items()]
    st.dataframe(pd.DataFrame(bank_details), use_container_width=True, hide_index=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="copyright">© {datetime.now().year} Cash Flow Analytics</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    app()