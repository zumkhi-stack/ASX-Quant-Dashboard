import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="Global Macro Forex Engine", layout="wide")
st.title("🏦 Institutional Forex Quantitative Command Center")

# --- GLOBAL FX TICKER TAPE ---
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{"symbols": [
  {"proName": "FX_IDC:AUDUSD", "title": "AUD / USD"},
  {"proName": "FX_IDC:AUDJPY", "title": "AUD / JPY"},
  {"proName": "FX_IDC:EURUSD", "title": "EUR / USD"},
  {"proName": "FX_IDC:GBPUSD", "title": "GBP / USD"},
  {"proName": "FX_IDC:USDJPY", "title": "USD / JPY"},
  {"proName": "FX_IDC:NZDUSD", "title": "NZD / USD"}
], "colorTheme": "light", "displayMode": "adaptive", "locale": "en"}
</script></div>""", height=50)

# --- FOREX TRACKED UNIVERSE ---
FOREX_MAJORS = [
    # Majors & G10 Drivers
    "AUDUSD=X", "AUDJPY=X", "EURUSD=X", "GBPUSD=X", "USDJPY=X", "NZDUSD=X", "USDCAD=X", "USDCHF=X",
    # Liquid Crosses
    "EURGBP=X", "EURJPY=X", "GBPJPY=X", "AUDNZD=X", "EURAUD=X", "GBPAUD=X",
    # Key Commodity/Emerging Proxies
    "USDSGD=X", "USDCNH=X", "USDMXN=X"
]

st.sidebar.header("🛡️ Global Forex Router")
raw_search = st.sidebar.text_input("Currency Search (e.g. AUDUSD, EURGBP)", "").strip().upper()

st.sidebar.markdown("---")
app_mode = st.sidebar.selectbox("Forex Workspace", [
    "Automated FX Fund Simulator",  
    "Central Bank Rate Matrix",       
    "Trend Momentum Screener",
    "WD Gann Mechanical Screener",
    "Interactive Charting Workspace"
])

# Normalize search string to Yahoo Finance format
if raw_search:
    target_ticker = f"{raw_search}=X" if not raw_search.endswith("=X") else raw_search
    clean_symbol = raw_search.replace("=X", "")
else:
    target_ticker = st.sidebar.selectbox("Select Active Pair", FOREX_MAJORS) if app_mode == "Interactive Charting Workspace" else FOREX_MAJORS[0]
    clean_symbol = target_ticker.replace("=X", "")

@st.cache_data(ttl=300)
def fetch_forex_dataset_pool(ticker_list):
    compiled_results = []
    if not ticker_list: return []
    try:
        t = Ticker(ticker_list)
        history = t.history(period="1y")
        if history is None or (isinstance(history, pd.DataFrame) and history.empty): return []
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

            r_name = tk.replace("=X", "")
            l_url = f"https://www.tradingview.com/chart/?symbol=FX:{r_name}"

            compiled_results.append({
                "Ticker": tk, "Chart Link": l_url, "Name": r_name, "Entry Price": p_prev, "Price": p_curr, 
                "Dist 52W High %": d_high, "is_bullish": is_bull, "Gann Signal": g_sig, "Current Candle Type": b_type
            })
        except: continue
    return compiled_results

# --- FX WORKSPACES INTERFACE ROUTING ---
if app_mode == "Automated FX Fund Simulator":
    st.header("🤖 Automated FX Sandbox Portfolio Allocation")
    max_risk = st.sidebar.slider("Max Execution Risk Stop %", 0.5, 5.0, 1.5, step=0.1)
    alloc_pool = st.sidebar.number_input("Sandbox Pool Capital ($ AUD)", value=50000)

    with st.spinner("Processing Strategy Matrix..."): data_pool = fetch_forex_dataset_pool(FOREX_MAJORS)
    if data_pool:
        df_p = pd.DataFrame(data_pool)
        top_positions = df_p.head(4).copy()
        
        cash = alloc_pool / len(top_positions)
        top_positions["Allocated Capital"] = cash
        top_positions["Stop Level"] = top_positions["Entry Price"] * (1 - (max_risk / 100))
        top_positions["Return %"] = ((top_positions["Price"] - top_positions["Entry Price"]) / top_positions["Entry Price"]) * 100
        top_positions["P&L ($)"] = (cash / top_positions["Entry Price"]) * (top_positions["Price"] - top_positions["Entry Price"])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Pairs Active", len(top_positions))
        c2.metric("Size Per Pair", f"${cash:,.2f}")
        c3.metric("Total P&L", f"${top_positions['P&L ($)'].sum():,.2f}")
        st.dataframe(top_positions[['Name', 'Entry Price', 'Price', 'Allocated Capital', 'P&L ($)', 'Return %', 'Stop Level']], hide_index=True, use_container_width=True)

elif app_mode == "Central Bank Rate Matrix":
    st.header("🏦 Global Central Bank Interest Yield Engine")
    rates_data = {
        "Country / Currency": ["United States (USD)", "Australia (AUD)", "Eurozone (EUR)", "United Kingdom (GBP)", "Japan (JPY)"],
        "Central Bank Interest Rate %": [5.25, 4.35, 4.00, 5.00, 0.25],
        "Macro Inflation %": [2.6, 3.4, 2.2, 2.0, 2.1]
    }
    st.dataframe(pd.DataFrame(rates_data), hide_index=True, use_container_width=True)

elif app_mode == "Trend Momentum Screener":
    st.header("🟢 Currency Momentum Alpha Screener")
    with st.spinner("Syncing Feed..."): data_pool = fetch_forex_dataset_pool(FOREX_MAJORS)
    if data_pool:
        st.data_editor(pd.DataFrame(data_pool)[['Name', 'Chart Link', 'Price', 'Gann Signal', 'Current Candle Type']], column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="%.4f")}, disabled=True, hide_index=True, use_container_width=True)

elif app_mode == "WD Gann Mechanical Screener":
    st.header("🦅 Advanced WD Gann Structural Currency Matrix")
    with st.spinner("Evaluating Swings..."): data_pool = fetch_forex_dataset_pool(FOREX_MAJORS)
    if data_pool:
        st.data_editor(pd.DataFrame(data_pool)[['Name', 'Chart Link', 'Gann Signal', 'Current Candle Type', 'Price']], column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="%.4f")}, disabled=True, hide_index=True, use_container_width=True)

elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Macro Deep Research Terminal: {clean_symbol}")
    with st.spinner("Pulling Pipeline..."): single_p = fetch_forex_dataset_pool([target_ticker])
    if single_p:
        sd = single_p[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Rate", f"{sd['Price']:.4f}")
        c2.metric("Gann Swing Direction", sd['Gann Signal'])
        c3.metric("Candle Structure", sd['Current Candle Type'])
        c4.metric("Trend (50/200MA)", "🚀 BULL" if sd['is_bullish'] else "⚠️ BEAR")

    components.html(f"""<div style="height:550px; width:100%;"><div id="tv_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "FX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});</script>
    </div>""", height=570)
