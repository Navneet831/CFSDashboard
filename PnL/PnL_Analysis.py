import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# =============================================================================
# CONFIGURATION & SETUP
# =============================================================================
FILE_PATH = r"C:\Users\hp\OneDrive\Desktop\Script\OPL\Base data\OPL FS Consolidate 0725.xlsx"
CRORE_CONVERSION = 10000000

PL_ITEMS = [
    'Revenue', 'Operating expense', 'Admin & Overheads', 'Employee Cost',
    'Other cost', 'EBITDA', 'Finance Costs', 'PAT'
]

# --- Theme & Colors ---
BG_PRIMARY = '#0f172a'
BG_SECONDARY = '#1e293b'
BG_TERTIARY = '#334155'
TEXT_PRIMARY = '#f1f5f9'
TEXT_SECONDARY = '#cbd5e1'
TEXT_MUTED = '#94a3b8'
ACCENT_PRIMARY = '#3b82f6'
ACCENT_SUCCESS = '#10b981'
ACCENT_DANGER = '#ef4444'
ACCENT_WARNING = '#f59e0b'
ACCENT_INFO = '#06b6d4'
BORDER_COLOR = '#334155'
GRADIENT_START = '#1e3a8a'
GRADIENT_END = '#7c3aed'

COLOR_MAP = {
    'Revenue': ACCENT_SUCCESS, 'Operating expense': ACCENT_DANGER,
    'Admin & Overheads': ACCENT_WARNING, 'Employee Cost': ACCENT_INFO,
    'Other cost': '#8b5cf6', 'EBITDA': ACCENT_PRIMARY,
    'Finance Costs': '#ef4444', 'PAT': '#10b981'
}

# =============================================================================
# DATA LOADING & PROCESSING
# =============================================================================
@st.cache_data(ttl=300)
def load_financial_data():
    """Loads only the P&L sheet from the specified Excel file."""
    try:
        pl_df = pd.read_excel(FILE_PATH, sheet_name='P&L')
        pl_df.columns = [str(col).strip().lower() for col in pl_df.columns]
        return {'P&L': pl_df}
    except Exception as e:
        st.error(f"Error loading P&L data from '{FILE_PATH}': {e}")
        return {}

def process_pl_data(pl_df):
    """
    Processes the P&L DataFrame to extract monthly and YTD data.
    Now fetches data from columns C to N (skipping B and O).
    """
    if pl_df is None or pl_df.empty:
        return {}, {}
    try:
        statement_col = pl_df.columns[0]
        
        # Get all columns except the first statement column
        all_data_cols = pl_df.columns[1:]
        
        # Filter out YTD columns
        non_ytd_cols = [col for col in all_data_cols if 'ytd' not in col.lower()]
        
        # Skip the first month column (index 0, which is column B) and take the next 12 months (C to N)
        # This gets columns at indices 1-12 from non_ytd_cols, which corresponds to C-N in Excel
        month_cols = non_ytd_cols[1:13] if len(non_ytd_cols) > 1 else []
        
        # Get YTD column (column O)
        ytd_col = next((col for col in pl_df.columns if 'ytd' in col.lower()), None)
        
        pl_data = {}
        ytd_data = {}
        
        for item in PL_ITEMS:
            matching_rows = pl_df[pl_df[statement_col].astype(str).str.contains(item, case=False, na=False)]
            
            if not matching_rows.empty:
                row = matching_rows.iloc[0]
                monthly_values = [pd.to_numeric(row.get(col, 0), errors='coerce') / CRORE_CONVERSION for col in month_cols]
                pl_data[item] = {
                    'months': [col.replace('-', ' ').title() for col in month_cols], 
                    'values': [v if pd.notna(v) else 0 for v in monthly_values]
                }
                
                if ytd_col and ytd_col in row:
                    ytd_val = pd.to_numeric(row[ytd_col], errors='coerce')
                    ytd_data[item] = ytd_val / CRORE_CONVERSION if pd.notna(ytd_val) else 0
                else:
                    ytd_data[item] = sum(pl_data[item]['values'])
            else:
                pass
                
    except Exception as e:
        st.error(f"An error occurred while processing P&L data: {e}")
        return {}, {}
        
    return pl_data, ytd_data

# =============================================================================
# UI & CHARTING FUNCTIONS
# =============================================================================
def create_metric_card(label, value, delta=None, value_color="neutral", prefix="₹", suffix=" Cr"):
    """Creates the HTML for a single metric card."""
    value_class = f"metric-value {value_color}"
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ""
    display_value = f"{value:.1f}%" if suffix == "%" else f"{prefix}{value:.2f}{suffix}"
    
    return f"""<div class="metric-card"><div class="metric-label">{label}</div><div class="{value_class}">{display_value}</div>{delta_html}</div>"""

def create_pl_trend_chart(pl_data):
    """Creates the main P&L trend chart."""
    if not pl_data:
        fig = go.Figure()
        fig.add_annotation(text="No P&L data available to display chart.", showarrow=False)
        fig.update_layout(plot_bgcolor=BG_SECONDARY, paper_bgcolor=BG_SECONDARY)
        return fig
        
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    for item in PL_ITEMS:
        if item in pl_data:
            data = pl_data[item]
            if item in ['Revenue', 'EBITDA', 'PAT']:
                fig.add_trace(go.Scatter(
                    x=data['months'], 
                    y=data['values'], 
                    mode='lines+markers', 
                    name=item, 
                    line=dict(color=COLOR_MAP.get(item, ACCENT_PRIMARY), width=3)
                ), secondary_y=True)
            else:
                fig.add_trace(go.Bar(
                    x=data['months'], 
                    y=[abs(v) for v in data['values']], 
                    name=item, 
                    marker_color=COLOR_MAP.get(item, ACCENT_DANGER), 
                    opacity=0.7
                ), secondary_y=False)
    
    fig.update_layout(
        title=dict(text='P&L Monthly Trends (Apr 24 - Mar 24)', font=dict(color=TEXT_PRIMARY, size=16)),
        xaxis=dict(title='Month', gridcolor=BORDER_COLOR, color=TEXT_SECONDARY),
        yaxis=dict(title='Costs (₹ Cr)', gridcolor=BORDER_COLOR, color=TEXT_SECONDARY),
        yaxis2=dict(title='Revenue/EBITDA/PAT (₹ Cr)', overlaying='y', side='right', gridcolor=BORDER_COLOR, color=TEXT_SECONDARY),
        height=450, barmode='group', plot_bgcolor=BG_SECONDARY, paper_bgcolor=BG_SECONDARY,
        font=dict(family="Inter", color=TEXT_PRIMARY), 
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    return fig

# =============================================================================
# MAIN APP FUNCTION (This is called by FR_main.py)
# =============================================================================
def app():
    """Renders the P&L Analysis content."""
    st.markdown("### YTD Performance")
    
    with st.spinner('Loading P&L data...'):
        financial_data = load_financial_data()
    
    if not financial_data or 'P&L' not in financial_data:
        st.error("❌ Could not load P&L data. Please verify the 'P&L' sheet exists in the Excel file.")
        return
        
    pl_data, ytd_data = process_pl_data(financial_data.get('P&L'))
    
    if ytd_data:
        cols = st.columns(4)
        for i, item in enumerate(PL_ITEMS):
            with cols[i % 4]:
                value = ytd_data.get(item, 0)
                is_positive_kpi = item in ['Revenue', 'EBITDA', 'PAT']
                
                if value == 0:
                    value_color = "neutral"
                elif is_positive_kpi:
                    value_color = "positive" if value > 0 else "negative"
                else: 
                    value_color = "negative"

                st.markdown(create_metric_card(item, value, delta="YTD", value_color=value_color), unsafe_allow_html=True)
        
        st.markdown('<div class="plot-container" style="margin-top: 1rem;">', unsafe_allow_html=True)
        pl_chart = create_pl_trend_chart(pl_data)
        st.plotly_chart(pl_chart, use_container_width=True, config={'displayModeBar': False})
        st.markdown('</div>', unsafe_allow_html=True)
        
        if ytd_data.get('Revenue', 0) > 0:
            st.markdown("### Key Ratios (YTD)")
            col1, col2, col3 = st.columns(3)
            with col1:
                margin = (ytd_data.get('EBITDA', 0) / ytd_data['Revenue']) * 100
                st.markdown(create_metric_card("EBITDA Margin", margin, value_color="positive" if margin > 0 else "negative", suffix="%"), unsafe_allow_html=True)
            with col2:
                total_costs = sum([abs(ytd_data.get(c, 0)) for c in ['Operating expense', 'Admin & Overheads', 'Employee Cost', 'Other cost']])
                cost_ratio = (total_costs / ytd_data['Revenue']) * 100
                st.markdown(create_metric_card("Cost-to-Revenue", cost_ratio, value_color="negative" if cost_ratio > 80 else "positive", suffix="%"), unsafe_allow_html=True)
            with col3:
                net_margin = (ytd_data.get('PAT', 0) / ytd_data['Revenue']) * 100
                st.markdown(create_metric_card("Net Profit Margin", net_margin, value_color="positive" if net_margin > 0 else "negative", suffix="%"), unsafe_allow_html=True)
    else:
        st.info("No processed P&L data to display.")

# =============================================================================
# STANDALONE EXECUTION BLOCK
# =============================================================================
if __name__ == "__main__":
    # This block only runs when the script is executed directly (streamlit run Pnl_Analysis.py)
    # It sets up the page config and styling that FR_main.py would normally handle.
    st.set_page_config(
        page_title="P&L Analysis Dashboard",
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        .stApp {{ background-color: {BG_PRIMARY}; color: {TEXT_PRIMARY}; }}
        * {{ font-family: 'Inter', sans-serif; }}
        .main-header {{ background: linear-gradient(135deg, {GRADIENT_START} 0%, {GRADIENT_END} 100%); padding: 1rem; border-radius: 10px; text-align: center; margin-bottom: 1rem; box-shadow: 0 8px 20px rgba(0,0,0,0.2); }}
        .main-header h1 {{ color: {TEXT_PRIMARY}; font-size: 1.5rem; font-weight: 700; margin: 0; }}
        .metric-card {{ background: {BG_SECONDARY}; padding: 1.25rem; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); border: 1px solid {BORDER_COLOR}; height: 100%; }}
        .metric-value {{ font-size: 1.5rem; font-weight: 700; margin: 0.5rem 0; }}
        .metric-value.positive {{ color: {ACCENT_SUCCESS}; }}
        .metric-value.negative {{ color: {ACCENT_DANGER}; }}
        .metric-value.neutral {{ color: {TEXT_PRIMARY}; }}
        .metric-label {{ color: {TEXT_MUTED}; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; }}
        .metric-delta {{ font-size: 0.75rem; margin-top: 0.5rem; }}
        .plot-container {{ background: {BG_SECONDARY}; padding: 1.25rem; border-radius: 10px; margin-bottom: 1rem; }}
        .footer {{ text-align: center; color: {TEXT_MUTED}; font-size: 0.75rem; margin-top: 1rem; padding: 0.5rem; border-top: 1px solid {BORDER_COLOR}; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown("<div class='main-header'><h1>📊 P&L Analysis Dashboard</h1></div>", unsafe_allow_html=True)
    
    # Call the main app function to render the content
    app()

    st.markdown(f"<div class='footer'>Last updated: {datetime.now().strftime('%Y-%m-%d')} | © Navneet Chaudhary </div>", unsafe_allow_html=True)