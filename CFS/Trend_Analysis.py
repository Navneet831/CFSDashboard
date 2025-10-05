import streamlit as st
import pandas as pd
import plotly.graph_objects as go
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
TEXT_SECONDARY = '#cbd5e1'
TEXT_MUTED = '#94a3b8'
ACCENT_SUCCESS = '#10b981'
ACCENT_DANGER = '#ef4444'
ACCENT_INFO = '#06b6d4'
BORDER_COLOR = '#334155'
GRADIENT_DEFAULT_START, GRADIENT_DEFAULT_END = '#1e3a8a', '#7c3aed'

st.set_page_config(page_title="Trend Analysis", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

def get_base_styles():
    return f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp {{ background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY}; }}
        * {{ font-family: 'Inter', sans-serif; }}
        .main-header {{ background: linear-gradient(135deg, {GRADIENT_DEFAULT_START} 0%, {GRADIENT_DEFAULT_END} 100%); padding: 1.5rem; border-radius: 16px; margin-bottom: 1.5rem; }}
        .main-header h1 {{ color: {TEXT_PRIMARY}; font-size: 1.75rem; font-weight: 700; margin: 0; }}
        .plot-container {{ background: {BG_SECONDARY}; padding: 2rem; border-radius: 16px; margin-bottom: 1.5rem; border: 1px solid {BORDER_COLOR}; }}
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
                        bank_data[bank_name] = pd.DataFrame({'Value_Date': pd.to_datetime(df.iloc[:, 2], errors='coerce'), 'Net_Flow': pd.to_numeric(df.iloc[:, 8], errors='coerce')}).dropna(subset=['Value_Date', 'Net_Flow'])
                    except Exception: pass
        return bank_data
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return {}

def consolidate_bank_data(bank_data, start_date, end_date):
    if not bank_data: return pd.DataFrame()
    df = pd.concat(list(bank_data.values())).query("@start_date <= Value_Date <= @end_date").copy()
    if df.empty: return pd.DataFrame()
    df['Withdrawal'] = df['Net_Flow'].apply(lambda x: abs(x) if x < 0 else 0)
    df['Deposit'] = df['Net_Flow'].apply(lambda x: x if x > 0 else 0)
    return df.sort_values('Value_Date')

def create_30_day_trend_chart(all_bank_data, end_date_dt):
    end_date = pd.Timestamp(end_date_dt)
    start_date = end_date - timedelta(days=29)
    consolidated_30day = consolidate_bank_data(all_bank_data, start_date, end_date)
    if consolidated_30day.empty:
        fig = go.Figure().add_annotation(text="No data for the last 30 days", showarrow=False)
        fig.update_layout(plot_bgcolor=BG_SECONDARY, paper_bgcolor=BG_SECONDARY, font_color=TEXT_PRIMARY)
        return fig
    daily_trend = consolidated_30day.groupby(consolidated_30day['Value_Date'].dt.date).agg({'Deposit': 'sum', 'Withdrawal': 'sum', 'Net_Flow': 'sum'}).reset_index()
    for col in ['Deposit', 'Withdrawal', 'Net_Flow']: daily_trend[col] /= CRORE_CONVERSION
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_trend['Value_Date'], y=daily_trend['Deposit'], name='Inflow', line=dict(color=ACCENT_SUCCESS, width=2), fill='tozeroy', fillcolor='rgba(16, 185, 129, 0.2)'))
    fig.add_trace(go.Scatter(x=daily_trend['Value_Date'], y=daily_trend['Withdrawal'], name='Outflow', line=dict(color=ACCENT_DANGER, width=2), fill='tozeroy', fillcolor='rgba(239, 68, 68, 0.2)'))
    fig.add_trace(go.Scatter(x=daily_trend['Value_Date'], y=daily_trend['Net_Flow'], name='Net Flow', line=dict(color=ACCENT_INFO, width=3, dash='dash'), yaxis='y2'))
    fig.update_layout(title_text="30-Day Cash Flow Trend", xaxis_title='Date', yaxis_title='Amount (₹ Crores)', yaxis2=dict(title="Net Flow (₹ Crores)", side='right', overlaying='y', showgrid=False), height=500, hovermode='x unified', plot_bgcolor=BG_SECONDARY, paper_bgcolor=BG_SECONDARY, font_color=TEXT_PRIMARY, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
    return fig

# =============================================================================
# MAIN APP LOGIC
# =============================================================================
def app():
    st.markdown(get_base_styles(), unsafe_allow_html=True)
    st.markdown("<div class='main-header'><h1>📈 Trend Analysis</h1></div>", unsafe_allow_html=True)

    bank_data = load_excel_data()
    if not bank_data: return

    all_dates = [d for df in bank_data.values() for d in df['Value_Date'].dropna()]
    if not all_dates:
        st.error("No valid dates found in data.")
        return

    min_date, max_date = min(all_dates).date(), max(all_dates).date()
    end_date_dt = st.date_input("Select End Date for 30-Day Trend", value=max_date, min_value=min_date, max_value=max_date, key='ta_end_date')

    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(create_30_day_trend_chart(bank_data, end_date_dt), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="copyright">© {datetime.now().year} Cash Flow Analytics</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    app()