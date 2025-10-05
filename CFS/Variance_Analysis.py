import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
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
ACCENT_PRIMARY = '#3b82f6'
ACCENT_WARNING = '#f59e0b'
BORDER_COLOR = '#334155'
GRADIENT_DEFAULT_START, GRADIENT_DEFAULT_END = '#1e3a8a', '#7c3aed'

st.set_page_config(page_title="Forecast Stacking", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

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
        bank_data, forecast_data = {}, pd.DataFrame()
        bank_name_mapping = {'sbi': 'SBI', 'icici': 'ICICI', 'hdfc': 'HDFC', 'federal': 'Federal', 'axis': 'Axis', 'yes': 'Yes', 'yes bank': 'Yes'}
        for sheet in xls.sheet_names:
            df, sheet_lower = pd.read_excel(xls, sheet_name=sheet), sheet.lower()
            if 'forecast' in sheet_lower:
                forecast_data = pd.DataFrame({'Forecast_Date': pd.to_datetime(df.iloc[:, 2], errors='coerce'), 'Net_Payable': pd.to_numeric(df.iloc[:, 6], errors='coerce'), 'Certainty': df.iloc[:, 15].fillna('Unknown')}).dropna(subset=['Forecast_Date'])
            else:
                bank_name = next((val for key, val in bank_name_mapping.items() if key in sheet_lower), None)
                if bank_name:
                    try:
                        bank_data[bank_name] = pd.DataFrame({'Value_Date': pd.to_datetime(df.iloc[:, 2], errors='coerce'), 'Net_Flow': pd.to_numeric(df.iloc[:, 8], errors='coerce')}).dropna(subset=['Value_Date', 'Net_Flow'])
                    except Exception: pass
        return bank_data, forecast_data
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        return {}, pd.DataFrame()

def consolidate_bank_data(bank_data, start_date, end_date):
    if not bank_data: return pd.DataFrame()
    return pd.concat(list(bank_data.values())).query("@start_date <= Value_Date <= @end_date")

def create_stacked_forecast_chart(consolidated_data, forecast_data, start_date, end_date):
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    if not forecast_data.empty:
        forecast_period = forecast_data.query("@start_date <= Forecast_Date <= @end_date").copy()
        if not forecast_period.empty:
            forecast_period['Certainty'] = forecast_period['Certainty'].str.lower()
            fixed = forecast_period.query("Certainty == 'fixed'").groupby('Forecast_Date')['Net_Payable'].sum().reset_index()
            contingency = forecast_period.query("Certainty == 'contingency'").groupby('Forecast_Date')['Net_Payable'].sum().reset_index()
            fig.add_trace(go.Bar(x=fixed['Forecast_Date'], y=fixed['Net_Payable'] / CRORE_CONVERSION, name='Fixed Forecast', marker_color=ACCENT_PRIMARY), secondary_y=False)
            fig.add_trace(go.Bar(x=contingency['Forecast_Date'], y=contingency['Net_Payable'] / CRORE_CONVERSION, name='Contingency Forecast', marker_color=ACCENT_WARNING), secondary_y=False)
    if not consolidated_data.empty:
        actuals_daily = consolidated_data.groupby(consolidated_data['Value_Date'].dt.date)['Net_Flow'].sum().reset_index()
        fig.add_trace(go.Scatter(x=actuals_daily['Value_Date'], y=actuals_daily['Net_Flow'] / CRORE_CONVERSION, mode='lines+markers', name='Actual', line=dict(color=ACCENT_SUCCESS, width=3)), secondary_y=True)
    fig.update_layout(title_text='Daily Forecast vs Actual Cash Flow (Stacked)', barmode='stack', height=500, hovermode='x unified', plot_bgcolor=BG_SECONDARY, paper_bgcolor=BG_SECONDARY, font_color=TEXT_PRIMARY, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1), xaxis_title='Date', yaxis_title='Forecast (₹ in Crores)', yaxis2=dict(title_text="Actual (₹ in Crores)", showgrid=False, overlaying='y', side='right'))
    return fig

# =============================================================================
# MAIN APP LOGIC
# =============================================================================
def app():
    st.markdown(get_base_styles(), unsafe_allow_html=True)
    st.markdown("<div class='main-header'><h1>📊 Forecast Stacking</h1></div>", unsafe_allow_html=True)

    bank_data, forecast_data = load_excel_data()
    if not bank_data: return

    all_dates = [d for df in bank_data.values() for d in df['Value_Date'].dropna()]
    if not all_dates:
        st.error("No valid dates found in data.")
        return

    min_date, max_date = min(all_dates).date(), max(all_dates).date()
    c1, c2 = st.columns(2)
    start_date_dt = c1.date_input("From Date", value=min_date, min_value=min_date, max_value=max_date, key='fs_start_date')
    end_date_dt = c2.date_input("To Date", value=max_date, min_value=start_date_dt, max_value=max_date, key='fs_end_date')
    
    start_date, end_date = pd.Timestamp(start_date_dt), pd.Timestamp(end_date_dt)
    consolidated_data = consolidate_bank_data(bank_data, start_date, end_date)

    st.markdown('<div class="plot-container">', unsafe_allow_html=True)
    st.plotly_chart(create_stacked_forecast_chart(consolidated_data, forecast_data, start_date, end_date), use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(f"""<div class="copyright">© {datetime.now().year} Cash Flow Analytics</div>""", unsafe_allow_html=True)

if __name__ == "__main__":
    app()