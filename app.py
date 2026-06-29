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
    try:
        t = Ticker(ticker_list)
        history = t.history(period="1y")
        summary = t.summary_detail
        financials = t.financial_data
        if history is None or (isinstance(history, dict) and not history): return []
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
                if ticker not in history.index.levels[0]: continue
                df = history.loc[ticker].dropna().copy()
            else:
                df = history.dropna().copy()

            if df.empty or len(df) < 50: continue

            # Technical overlays
            df['50_MA'] = df['adjclose'].rolling(window=50).mean()
            df['200_MA'] = df['adjclose'].rolling(window=200).mean()
            latest_close = float(df['adjclose'].iloc[-1])
            prev_close = float(df['adjclose'].iloc[-2]) if len(df) > 1 else latest_close
            high_52w = float(df['high'].max())
            dist_to_high = ((high_52w - latest_close) / high_52w) * 100
            distance_usd = high_52w - latest_close
            is_bullish_trend = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1])

            # Candle structures
            df['prev_high'] = df['high'].shift(1)
            df['prev_low'] = df['low'].shift(1)
            last_row = df.iloc[-1]
            h, l, ph, pl = last_row['high'], last_row['low'], last_row['prev_high'], last_row['prev_low']

            if h > ph and l < pl: bar_type = "🟠 Outside Bar"
            elif h <= ph and l >= pl: bar_type = "⚪ Inside Bar"
            elif h > ph and l >= pl: bar_type = "🟢 Up Bar"
            else: bar_type = "🔴 Down Bar"

            # Gann System Mechanics
            swing_dir = 1
            for i in range(2, len(df)):
                if df['high'].iloc[i] > df['high'].iloc[i-2] and swing_dir == -1: swing_dir = 1
                elif df['low'].iloc[i] < df['low'].iloc[i-2] and swing_dir == 1: swing_dir = -1

            gann_signal = "🟢 GANN UP-SWING" if swing_dir == 1 else "🚨 GANN DOWN-SWING"
            if is_cycle_node: gann_signal += f" ⚡{node_type}"

            tick_summary = summary.get(ticker, {}) if summary else {}
            tick_fin = financials.get(ticker, {}) if financials else {}
            raw_name = ticker.replace(".AX", "").replace("=X", "")
            
            # Smart URL Routing for TradingView redirects
            if "=X" in ticker:
                link_url = f"https://www.tradingview.com/chart/?symbol=FX:{raw_name}"
            else:
                link_url = f"https://www.tradingview.com/chart/?symbol=ASX:{raw_name}"

            compiled_results.append({
                "Ticker": ticker, "Chart Link": link_url, "Name": raw_name, "Entry Price": prev_close, "Price": latest_close, 
                "Dist 52W High %": dist_to_high, "Distance to Peak ($)": distance_usd, "is_bullish": is_bullish_trend,
                "Gann Signal": gann_signal, "Current Candle Type": bar_type, 
                "Trailing P/E": tick_summary.get('trailingPE', np.nan),
                "Profit Margin %": tick_fin.get('profitMargins', np.nan) * 100 if tick_fin.get('profitMargins', np.nan) else np.nan,
                "Div Yield %": tick_summary.get('dividendYield', np.nan) * 100 if tick_summary.get('dividendYield', np.nan) else np.nan
            })
        except Exception: continue
    return compiled_results

# --- EXECUTE WORKSPACE ROUTING ---

if app_mode == "Automated Quant Fund Simulator":
    st.header(f"🤖 Multi-Asset Quant Management Simulator ({market_tier})")
    st.sidebar.subheader("⚙️ Quant System Tuning")
    max_risk = st.sidebar.slider("Maximum Trailing Stop-Loss %", 1.0, 15.0, 5.0, step=0.5)
    allocation_pool = st.sidebar.number_input("Total Sandbox Capital ($ AUD)", value=20000, step=1000)

    with st.spinner("Analyzing assets..."):
        data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        res_df = pd
