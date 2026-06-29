import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Global Multi-Asset Quant Engine", layout="wide")
st.title("📊 ASX & Forex Master Quantitative Command Center")

# --- TICKER TAPE ---
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{"symbols": [{"proName": "INDEX:XJO", "title": "ASX 200"}, {"proName": "FX_IDC:AUDUSD", "title": "AUD/USD"}, {"proName": "FX_IDC:AUDJPY", "title": "AUD/JPY"}, {"proName": "SP:SPX", "title": "S&P 500"}], "colorTheme": "light", "displayMode": "adaptive", "locale": "en"}
</script></div>""", height=50)

ASX_50 = ["BHP.AX", "CBA.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "MQG.AX", "WES.AX", "RIO.AX", "FMG.AX", "CSL.AX", "WDS.AX", "TLS.AX", "TCL.AX", "WOW.AX", "QBE.AX", "GMG.AX", "MIN.AX", "APA.AX", "QAN.AX", "SPK.AX", "REA.AX", "ALL.AX", "SHL.AX", "COH.AX", "IPL.AX", "BSL.AX", "PPT.AX", "WHC.AX", "ALQ.AX", "LYC.AX", "BEN.AX", "BOQ.AX", "BLD.AX", "CAR.AX", "SGP.AX", "DXS.AX", "CHC.AX", "GPT.AX", "MGR.AX", "VCX.AX", "AZJ.AX", "A2M.AX", "AMP.AX", "ANN.AX", "AST.AX", "ALX.AX", "EVN.AX", "IAG.AX", "MPL.AX", "SUN.AX"]
FOREX_MAJORS = ["AUDUSD=X", "AUDJPY=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X", "NZDUSD=X"]

st.sidebar.header("🛡️ Domain Selector")
market_tier = st.sidebar.selectbox("Market Target", ["ASX 50 Blue Chips", "Global Macro Forex Pairs", "Multi-Asset Hybrid Pool"])

if market_tier == "ASX 50 Blue Chips":
    active_universe, is_forex_only = ASX_50, False
elif market_tier == "Global Macro Forex Pairs":
    active_universe, is_forex_only = FOREX_MAJORS, True
else:
    active_universe, is_forex_only = ASX_50 + FOREX_MAJORS, False

raw_search = st.sidebar.text_input("Deep Research Search", "").strip().upper()
app_mode = st.sidebar.selectbox("App Workspace", ["Automated Quant Fund Simulator", "Global Macro Forex Router", "Trend Momentum Screener", "Fundamental Value Searcher", "WD Gann Mechanical Screener", "Interactive Charting Workspace"])

if raw_search:
    if any(fx in raw_search for fx in ["USD", "JPY", "EUR", "GBP", "AUD", "NZD"]):
        target_ticker = f"{raw_search}=X" if not raw_search.endswith("=X") else raw_search
        clean_symbol = raw_search.replace("=X", "")
    else:
        target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
        clean_symbol = raw_search.split('.')[0]
else:
    target_ticker = st.sidebar.selectbox("Select Asset", active_universe) if app_mode == "Interactive Charting Workspace" else active_universe[0]
    clean_symbol = target_ticker.replace(".AX", "").replace("=X", "")

@st.cache_data(ttl=300)
def fetch_master_dataset_pool(ticker_list):
    compiled_results = []
    if not ticker_list: return []
    try:
        t = Ticker(ticker_list)
        history = t.history(period="1y")
        if history is None or (isinstance(history, pd.DataFrame) and history.empty): return []
        summary, financials = t.summary_detail, t.financial_data
    except: return []

    cm, cd = datetime.now().month, datetime.now().day
    is_node, n_type = False, ""
    for m, d, t_name in [(3,21,"CARDINAL"),(6,22,"CARDINAL"),(9,23,"CARDINAL"),(12,22,"CARDINAL"),(2,4,"FIXED"),(5,6,"FIXED"),(8,9,"FIXED"),(11,7,"FIXED")]:
        if cm == m and abs(cd - d) <= 2: is_node, n_type = True, f" [{t_name}]"

    for tk in ticker_list:
        try:
            if isinstance(history.index, pd.MultiIndex):
                if tk not in history.index.levels[0]: continue
                df = history.loc[tk].dropna().copy()
            else: df = history.dropna().copy()
            if df.empty or len(df) < 5: continue

            c_col = 'adjclose' if 'adjclose' in df.columns else 'close'
            df['50_MA'] = df[c_col].rolling(window=min(50, len(df))).mean()
            df['200_MA'] = df[c_col].rolling(window=min(200, len(df))).mean()
            
            p_curr, p_prev = float(df[c_col].iloc[-1]), float(df[c_col].iloc[-2]) if len(df) > 1 else float(df[c_col].iloc[-1])
            h_52w = float(df['high'].max())
            d_high = ((h_52w - p_curr) / h_52w) * 100 if h_52w > 0 else 0
            is_bull = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1]) if len(df) >= 50 else True

            df['ph'], df['pl'] = df['high'].shift(1), df['low'].shift(1)
            lr = df.iloc[-1]
            h, l, ph, pl = lr['high'], lr['low'], lr['ph'], lr['pl']
            b_type = "🟠 Outside Bar" if (h > ph and l < pl) else ("⚪ Inside Bar" if (h <= ph and l >= pl) else ("🟢 Up Bar" if h > ph else "🔴 Down Bar"))

            s_dir = 1
            for i in range(2, len(df)):
                if df['high'].iloc[i] > df['high'].iloc[i-2] and s_dir == -1: s_dir = 1
                elif df['low'].iloc[i] < df['low'].iloc[i-2] and s_dir == 1: s_dir = -1
            g_sig = f"🟢 GANN UP" if s_dir == 1 else "🚨 GANN DOWN"
            if is_node: g_sig += f" ⚡{n_type}"

            t_sum = summary.get(tk, {}) if isinstance(summary, dict) else {}
            t_fin = financials.get(tk, {}) if isinstance(financials, dict) else {}
            r_name = tk.replace(".AX", "").replace("=X", "")
            l_url = f"https://www.tradingview.com/chart/?symbol={'FX' if '=X' in tk else 'ASX'}:{r_name}"

            compiled_results.append({
                "Ticker": tk, "Chart Link": l_url, "Name": r_name, "Entry Price": p_prev, "Price": p_curr, 
                "Dist 52W High %": d_high, "is_bullish": is_bull = True, "Gann Signal": g_sig, "Current Candle Type": b_type, 
                "Trailing P/E": t_sum.get('trailingPE', np.nan),
                "Profit Margin %": t_fin.get('profitMargins', np.nan) * 100 if t_fin.get('profitMargins') else np.nan,
                "Div Yield %": t_sum.get('dividendYield', np.nan) * 100 if t_sum.get('dividendYield') else np.nan
            })
        except: continue
    return compiled_results

# --- APP WORKSPACES ROUTING ---
if app_mode == "Automated Quant Fund Simulator":
    st.header(f"🤖 Quant Simulator ({market_tier})")
    max_risk = st.sidebar.slider("Max Trailing Stop-Loss %", 1.0, 15.0, 5.0, step=0.5)
    alloc_pool = st.sidebar.number_input("Sandbox Capital ($ AUD)", value=20000)

    with st.spinner("Syncing Engine..."): data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        df_p = pd.DataFrame(data_pool)
        top_5 = df_p if is_forex_only else df_p[(df_p["is_bullish"]==True) & (df_p["Gann Signal"].str.contains("UP"))].sort_values(by="Dist 52W High %").head(5)
        if not top_5.empty:
            cash = alloc_pool / len(top_5)
            top_5["Allocated Capital"] = cash
            top_5["Stop Level"] = top_5["Entry Price"] * (1 - (max_risk / 100))
            top_5["Return %"] = ((top_5["Price"] - top_5["Entry Price"]) / top_5["Entry Price"]) * 100
            top_5["P&L ($)"] = (cash / top_5["Entry Price"]) * (
