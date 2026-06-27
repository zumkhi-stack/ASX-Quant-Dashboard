import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ASX Master Quant Command Center", layout="wide")
st.title("📊 ASX Master Quantitative & Geometric Command Center")

# --- CORE DATA TIERS ---
ASX_50 = [
    "BHP.AX", "CBA.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "MQG.AX", "WES.AX", "RIO.AX", "FMG.AX", "CSL.AX",
    "WDS.AX", "TLS.AX", "TCL.AX", "WOW.AX", "QBE.AX", "GMG.AX", "MIN.AX", "APA.AX", "QAN.AX", "SPK.AX",
    "REA.AX", "ALL.AX", "SHL.AX", "COH.AX", "IPL.AX", "BSL.AX", "PPT.AX", "WHC.AX", "ALQ.AX", "LYC.AX",
    "BEN.AX", "BOQ.AX", "BLD.AX", "CAR.AX", "SGP.AX", "DXS.AX", "CHC.AX", "GPT.AX", "MGR.AX", "VCX.AX",
    "AZJ.AX", "A2M.AX", "AMP.AX", "ANN.AX", "AST.AX", "ALX.AX", "EVN.AX", "IAG.AX", "MPL.AX", "SUN.AX"
]

# --- SIDEBAR MATRICES & DYNAMIC SEARCH ---
st.sidebar.header("🔍 Global Market Router")
raw_search = st.sidebar.text_input("Deep Research Search (e.g. PLS, REA, DRO)", "").strip().upper()

st.sidebar.markdown("---")
st.sidebar.header("🎯 Navigation Matrix")
app_mode = st.sidebar.selectbox("Choose App Workspace", [
    "Trend Momentum Screener",
    "Fundamental Value Searcher",
    "WD Gann Mechanical Screener",
    "Interactive Charting Workspace",
    "Target Stock Deep Research"
])

if raw_search:
    target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
    clean_symbol = raw_search.split('.')[0]
    if app_mode not in ["Trend Momentum Screener", "Fundamental Value Searcher", "WD Gann Mechanical Screener"]:
        app_mode = "Target Stock Deep Research"
else:
    if app_mode == "Interactive Charting Workspace":
        ticker_choice = st.sidebar.selectbox("Select Core Portfolio Ticker", ASX_50)
        clean_symbol = ticker_choice.split('.')[0]
        target_ticker = ticker_choice
    else:
        target_ticker = "BHP.AX"
        clean_symbol = "BHP"

tv_direct_url = f"https://www.tradingview.com/chart/?symbol=ASX%3A{clean_symbol}"

st.sidebar.markdown("---")
st.sidebar.header("🚀 Personal Pine Scripts Gateway")
st.sidebar.link_button(f"🔓 Open {clean_symbol} Workspace", tv_direct_url, type="primary", use_container_width=True)

# --- MASTER PIPELINE ENGINE ---
@st.cache_data(ttl=300)  # Extended to 5 mins to help prevent morning server overloads
def fetch_master_dataset_pool(ticker_list):
    compiled_results = []
    try:
        t = Ticker(ticker_list)
        history = t.history(period="1y")
        summary = t.summary_detail
        financials = t.financial_data
        
        # Check if we got valid data back from Yahoo
        if history is None or (isinstance(history, dict) and not history):
            return []
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

            df['50_MA'] = df['adjclose'].rolling(window=50).mean()
            df['200_MA'] = df['adjclose'].rolling(window=200).mean()
            latest_close = float(df['adjclose'].iloc[-1])
            high_52w = float(df['high'].max())
            dist_to_high = ((high_52w - latest_close) / high_52w) * 100
            
            distance_usd = high_52w - latest_close
            is_bullish_trend = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1])

            df['prev_high'] = df['high'].shift(1)
            df['prev_low'] = df['low'].shift(1)
            last_row = df.iloc[-1]
            h, l, ph, pl = last_row['high'], last_row['low'], last_row['prev_high'], last_row['prev_low']

            if h > ph and l < pl: bar_type = "🟠 Outside Bar (Volatility)"
            elif h <= ph and l >= pl: bar_type = "⚪ Inside Bar (Consolidation)"
            elif h > ph and l >= pl: bar_type = "🟢 Up Bar (Bullish)"
            else: bar_type = "🔴 Down Bar (Bearish)"

            swing_dir = 1
            for i in range(2, len(df)):
                prev2 = df.iloc[i-2]
                curr = df.iloc[i]
                if curr['high'] > prev2['high'] and swing_dir == -1: swing_dir = 1
                elif curr['low'] < prev2['low'] and swing_dir == 1: swing_dir = -1

            gann_signal = "🟢 GANN UP-SWING" if swing_dir == 1 else "🚨 GANN DOWN-SWING"
            if is_cycle_node: gann_signal += f" ⚡{node_type}"

            tick_summary = summary.get(ticker, {})
            tick_fin = financials.get(ticker, {})

            raw_name = ticker.split('.')[0]
            link_url = f"https://www.tradingview.com/chart/?symbol=ASX%3A{raw_name}"

            compiled_results.append({
                "Ticker": ticker,
                "Chart Link": link_url,
                "Name": raw_name,
                "Price": latest_close, 
                "Dist 52W High %": dist_to_high, 
                "Distance to Peak ($)": distance_usd,
                "is_bullish": is_bullish_trend,
                "Gann Signal": gann_signal, "Current Candle Type": bar_type,
                "Trailing P/E": tick_summary.get('trailingPE', np.nan),
                "Profit Margin %": tick_fin.get('profitMargins', np.nan) * 100 if tick_fin.get('profitMargins', np.nan) else np.nan,
                "Div Yield %": tick_summary.get('dividendYield', np.nan) * 100 if tick_summary.get('dividendYield', np.nan) else np.nan
            })
        except Exception:
            continue
    return compiled_results

# --- APP WORKSPACE ROUTING CHANNELS ---

if app_mode == "Trend Momentum Screener":
    st.header("🟢 Original Elite Momentum Screener (ASX 50)")
    st.info("💡 Tip: Click any link under the 'Chart Link' column to open that specific stock directly in TradingView.")
    
    with st.spinner("Processing original trend filters..."):
        data_pool = fetch_master_dataset_pool(ASX_50)
        
    if data_pool:
        res_df = pd.DataFrame(data_pool)
        filtered = res_df[(res_df["is_bullish"] == True) & (res_df["Dist 52W High %"] <= 15.0)].copy()

        st.data_editor(
            filtered[['Name', 'Chart Link', 'Price', 'Dist 52W High %', 'Distance to Peak ($)']],
            column_config={
                "Chart Link": st.column_config.LinkColumn("Open Workspace", display_text="📈 Launch TV Chart"),
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Dist 52W High %": st.column_config.NumberColumn(format="%.2f%%"),
                "Distance to Peak ($)": st.column_config.NumberColumn("Distance to Peak ($)", format="$%.2f")
            },
            disabled=True, hide_index=True, use_container_width=True
        )
    else:
        st.error("⚠️ Yahoo Finance is temporarily congested or blocking this cloud instance connection.")
        if st.button("🔄 Force Reconnect & Retry Now", type="primary"):
            st.rerun()

elif app_mode == "Fundamental Value Searcher":
    st.header("💎 Fundamental Balance Sheet Matrix")
    with st.spinner("Extracting corporate reports..."):
        data_pool = fetch_master_dataset_pool(ASX_50)
        
    if data_pool:
        res_df = pd.DataFrame(data_pool).copy()
        st.data_editor(
            res_df[['Name', 'Chart Link', 'Price', 'Trailing P/E', 'Profit Margin %', 'Div Yield %']],
            column_config={
                "Chart Link": st.column_config.LinkColumn("Open Workspace", display_text="📈 Launch TV Chart"),
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Profit Margin %": st.column_config.NumberColumn(format="%.2f%%"),
                "Div Yield %": st.column_config.NumberColumn(format="%.2f%%")
            },
            disabled=True, hide_index=True, use_container_width=True
        )
    else:
        st.error("⚠️ Yahoo Finance is temporarily congested or blocking this cloud instance connection.")
        if st.button("🔄 Force Reconnect & Retry Now", type="primary"):
            st.rerun()

elif app_mode == "WD Gann Mechanical Screener":
    st.header("🦅 Advanced WD Gann Structural Matrix")
    gann_filter = st.radio("Isolate Swing Layers", ["All Matrix Assets", "Up-Swings Only", "Volatility Breaks"], horizontal=True)

    with st.spinner("Calculating geometric pivots..."):
        data_pool = fetch_master_dataset_pool(ASX_50)
        
    if data_pool:
        res_df = pd.DataFrame(data_pool)
        if gann_filter == "Up-Swings Only":
            res_df = res_df[res_df["Gann Signal"].str.contains("UP-SWING")]
        elif gann_filter == "Volatility Breaks":
            res_df = res_df[res_df["Current Candle Type"].str.contains("Outside")]

        st.data_editor(
            res_df[['Name', 'Chart Link', 'Gann Signal', 'Current Candle Type', 'Price', 'Dist 52W High %']],
            column_config={
                "Chart Link": st.column_config.LinkColumn("Open Workspace", display_text="📈 Launch TV Chart"),
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Dist 52W High %": st.column_config.NumberColumn(format="%.2f%%")
            },
            disabled=True, hide_index=True, use_container_width=True
        )
    else:
        st.error("⚠️ Yahoo Finance is temporarily congested or blocking this cloud instance connection.")
        if st.button("🔄 Force Reconnect & Retry Now", type="primary"):
            st.rerun()

elif app_mode == "Interactive Charting Workspace" or app_mode == "Target Stock Deep Research":
    st.header(f"📈 Deep Research & Charting Terminal: ASX:{clean_symbol}")
    with st.spinner(f"Pulling real-time profile data for {clean_symbol}..."):
        single_pool = fetch_master_dataset_pool([target_ticker])
        
    if single_pool:
        sd = single_pool[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Close", f"${sd['Price']:.2f}")
        c2.metric("Gann Swing Direction", sd['Gann Signal'])
        c3.metric("Candle Structure", sd['Current Candle Type'])
        c4.metric("Trend State (50/200MA)", "🚀 BULLISH" if sd['is_bullish'] else "⚠️ BEARISH")
    else:
        st.warning("Could not pull real-time API metrics for this specific ticker code right now, but loading live chart view below...")

    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:550px; width:100%;"><div id="tradingview_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "ASX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tradingview_chart"}});
      </script>
    </div>
    """
    components.html(tradingview_html, height=570)
