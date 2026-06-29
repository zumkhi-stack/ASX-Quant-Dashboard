import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="Global Multi-Asset Quant Engine", layout="wide")
st.title("📊 ASX & Forex Master Quantitative Command Center")

# --- GLOBAL MARKET TICKER TAPE ---
ticker_tape_html = """
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    {"proName": "INDEX:XJO", "title": "Australia (ASX 200)"},
    {"proName": "FX_IDC:AUDUSD", "title": "AUD / USD"},
    {"proName": "FX_IDC:AUDJPY", "title": "AUD / JPY"},
    {"proName": "SP:SPX", "title": "USA (S&P 500)"},
    {"proName": "NASDAQ:IXIC", "title": "USA (Nasdaq)"},
    {"proName": "NSE:NIFTY", "title": "India (Nifty 50)"}
  ],
  "showSymbolLogo": true,
  "colorTheme": "light",
  "isTransparent": false,
  "displayMode": "adaptive",
  "locale": "en"
}
  </script>
</div>
"""
components.html(ticker_tape_html, height=50)

# --- TRACKED UNIVERSE ASSETS ---
ASX_50 = [
    "BHP.AX", "CBA.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "MQG.AX", "WES.AX", "RIO.AX", "FMG.AX", "CSL.AX",
    "WDS.AX", "TLS.AX", "TCL.AX", "WOW.AX", "QBE.AX", "GMG.AX", "MIN.AX", "APA.AX", "QAN.AX", "SPK.AX",
    "REA.AX", "ALL.AX", "SHL.AX", "COH.AX", "IPL.AX", "BSL.AX", "PPT.AX", "WHC.AX", "ALQ.AX", "LYC.AX",
    "BEN.AX", "BOQ.AX", "BLD.AX", "CAR.AX", "SGP.AX", "DXS.AX", "CHC.AX", "GPT.AX", "MGR.AX", "VCX.AX",
    "AZJ.AX", "A2M.AX", "AMP.AX", "ANN.AX", "AST.AX", "ALX.AX", "EVN.AX", "IAG.AX", "MPL.AX", "SUN.AX"
]

FOREX_MAJORS = [
    "AUDUSD=X", "AUDJPY=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X", "NZDUSD=X"
]

# --- SIDEBAR PORTFOLIO CONTROLS ---
st.sidebar.header("🛡️ Strategy Domain Selector")
market_tier = st.sidebar.selectbox("Choose Core Market Target", [
    "ASX 50 Blue Chips", 
    "Global Macro Forex Pairs",
    "Multi-Asset Hybrid Pool (Equities + FX)"
])

# Route data stream allocations dynamically
if market_tier == "ASX 50 Blue Chips":
    active_universe = ASX_50
    is_forex_only = False
elif market_tier == "Global Macro Forex Pairs":
    active_universe = FOREX_MAJORS
    is_forex_only = True
else:
    active_universe = ASX_50 + FOREX_MAJORS
    is_forex_only = False

st.sidebar.markdown("---")
st.sidebar.header("🔍 Global Market Router")
raw_search = st.sidebar.text_input("Deep Research Search (e.g. PLS, REA, AUDUSD)", "").strip().upper()

st.sidebar.markdown("---")
st.sidebar.header("🎯 Navigation Matrix")
app_mode = st.sidebar.selectbox("Choose App Workspace", [
    "Automated Quant Fund Simulator",  
    "Global Macro Forex Router",       
    "Trend Momentum Screener",
    "Fundamental Value Searcher",      
    "WD Gann Mechanical Screener",
    "Interactive Charting Workspace",
    "Target Stock Deep Research"
])

# Search normalization filter logic
if raw_search:
    if any(fx in raw_search for fx in ["USD", "JPY", "EUR", "GBP", "AUD", "NZD"]):
        target_ticker = f"{raw_search}=X" if not raw_search.endswith("=X") else raw_search
        clean_symbol = raw_search.replace("=X", "")
    else:
        target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
        clean_symbol = raw_search.split('.')[0]
    
    if app_mode not in ["Global Macro Forex Router", "Trend Momentum Screener", "Fundamental Value Searcher", "WD Gann Mechanical Screener", "Automated Quant Fund Simulator"]:
        app_mode = "Target Stock Deep Research"
else:
    if app_mode == "Interactive Charting Workspace":
        ticker_choice = st.sidebar.selectbox("Select Active Ticker Pool Asset", active_universe)
        clean_symbol = ticker_choice.replace(".AX", "").replace("=X", "")
        target_ticker = ticker_choice
    else:
        target_ticker = active_universe[0]
        clean_symbol = target_ticker.replace(".AX", "").replace("=X", "")

# --- MASTER PIPELINE ENGINE ---
@st.cache_data(ttl=300)
def fetch_master_dataset_pool(ticker_list):
    compiled_results = []
    if not ticker_list:
        return compiled_results
        
    try:
        t = Ticker(ticker_list)
        history = t.history(period="1y")
        if history is None or (isinstance(history, dict) and not history) or (isinstance(history, pd.DataFrame) and history.empty): 
            return []
            
        summary = t.summary_detail
        financials = t.financial_data
    except Exception:
        return []

    today = datetime.now()
    cm, cd = today.month, today.day
    is_cycle_node = False
    node_type = ""

    cardinal_nodes = [(3,21), (6,22), (9,23), (12,22)]
    fixed_nodes    = [(2,4), (5,6), (8,9), (11,7)]
    inter_nodes    = [(1,5), (1,20), (2,19), (3,6), (4,5), (4,20), (5,21), (6,6),
                      (7,7), (7,23), (8,23), (9,7), (10,8), (10,23), (11,22), (12,7)]

    for m, d in cardinal_nodes:
        if cm == m and abs(cd - d) <= 2: is_cycle_node, node_type = True, " [CARDINAL]"
    for m, d in fixed_nodes:
        if cm == m and abs(cd - d) <= 2: is_cycle_node, node_type = True, " [FIXED]"
    for m, d in inter_nodes:
        if cm == m and abs(cd - d) <= 2: is_cycle_node, node_type = True, " [INTERMEDIATE]"

    for ticker in ticker_list:
        try:
            if isinstance(history.index, pd.MultiIndex):
                tk_match = ticker
                if ticker not in history.index.levels[0]:
                    if ticker.lower() in history.index.levels[0]: tk_match = ticker.lower()
                    elif ticker.upper() in history.index.levels[0]: tk_match = ticker.upper()
                    else: continue
                df = history.loc[tk_match].dropna().copy()
            else:
                df = history.dropna().copy()

            if df.empty or len(df) < 10: continue

            close_col = 'adjclose' if 'adjclose' in df.columns else 'close'
            
            df['50_MA'] = df[close_col].rolling(window=min(50, len(df))).mean()
            df['200_MA'] = df[close_col].rolling(window=min(200, len(df))).mean()
            latest
