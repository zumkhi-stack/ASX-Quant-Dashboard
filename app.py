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
    "Automated Quant Fund Simulator",  
    "Global Macro Forex Router",       # <-- Restored selection path
    "Trend Momentum Screener",
    "Fundamental Value Searcher",
    "WD Gann Mechanical Screener",
    "Interactive Charting Workspace",
    "Target Stock Deep Research"
])

if raw_search:
    target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
    clean_symbol = raw_search.split('.')[0]
    if app_mode not in ["Global Macro Forex Router", "Trend Momentum Screener", "Fundamental Value Searcher", "WD Gann Mechanical Screener", "Automated Quant Fund Simulator"]:
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

            df['50_MA'] = df['adjclose'].rolling(window=50).mean()
            df['200_MA'] = df['adjclose'].rolling(window=200).mean()
            latest_close = float(df['adjclose'].iloc[-1])
            prev_close = float(df['adjclose'].iloc[-2]) if len(df) > 1 else latest_close
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
                "Ticker": ticker, "Chart Link": link_url, "Name": raw_name, "Entry Price": prev_close, "Price": latest_close, 
                "Dist 52W High %": dist_to_high, "Distance to Peak ($)": distance_usd, "is_bullish": is_bullish_trend,
                "Gann Signal": gann_signal, "Current Candle Type": bar_type, "Trailing P/E": tick_summary.get('trailingPE', np.nan),
                "Profit Margin %": tick_fin.get('profitMargins', np.nan) * 100 if tick_fin.get('profitMargins', np.nan) else np.nan,
                "Div Yield %": tick_summary.get('dividendYield', np.nan) * 100 if tick_summary.get('dividendYield', np.nan) else np.nan
            })
        except Exception: continue
    return compiled_results

# --- APP WORKSPACE ROUTING CHANNELS ---

if app_mode == "Automated Quant Fund Simulator":
    st.header("🤖 Automated Quant Management Simulator (Top 5 Allocation Loop)")
    st.markdown("This system evaluates live trend metrics every day and algorithmically maintains a strict **5-Stock Portfolio** based on mathematical indicators, managing stops and allocations without human emotion.")

    st.sidebar.subheader("⚙️ Quant System Tuning")
    max_risk = st.sidebar.slider("Maximum Trailing Stop-Loss %", 3.0, 15.0, 7.5, step=0.5)
    allocation_pool = st.sidebar.number_input("Total Sandbox Capital ($ AUD)", value=20000, step=1000)

    with st.spinner("Executing rule engine across ASX 50 pool..."):
        data_pool = fetch_master_dataset_pool(ASX_50)

    if data_pool:
        res_df = pd.DataFrame(data_pool)
        quant_targets = res_df[(res_df["is_bullish"] == True) & (res_df["Gann Signal"].str.contains("UP-SWING"))].copy()
        quant_targets = quant_targets.sort_values(by="Dist 52W High %", ascending=True)
        top_5_portfolio = quant_targets.head(5).copy()
        
        if not top_5_portfolio.empty:
            per_stock_cash = allocation_pool / 5
            top_5_portfolio["Allocated Capital"] = per_stock_cash
            top_5_portfolio["Units"] = (per_stock_cash / top_5_portfolio["Entry Price"]).astype(int)
            top_5_portfolio["Hard Stop-Loss Price"] = top_5_portfolio["Entry Price"] * (1 - (max_risk / 100))
            top_5_portfolio["Return %"] = ((top_5_portfolio["Price"] - top_5_portfolio["Entry Price"]) / top_5_portfolio["Entry Price"]) * 100
            top_5_portfolio["Current P&L ($)"] = top_5_portfolio["Units"] * (top_5_portfolio["Price"] - top_5_portfolio["Entry Price"])
            
            total_pnl = top_5_portfolio["Current P&L ($)"].sum()
            total_return = (total_pnl / allocation_pool) * 100
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Active Capital Slots Used", f"{len(top_5_portfolio)} / 5 Loaded", "Fully Deployed")
            m2.metric("Sizing Weight Per Asset", f"${per_stock_cash:,.2f} AUD")
            if total_pnl >= 0: m3.metric("Total Fund P&L", f"+${total_pnl:,.2f} AUD", f"🟢 +{total_return:.2f}%")
            else: m3.metric("Total Fund P&L", f"-${abs(total_pnl):,.2f} AUD", f"🔴 {total_return:.2f}%")

            st.subheader("💼 Active System Portfolios (Auto-Selected Entries)")
            st.data_editor(
                top_5_portfolio[['Name', 'Entry Price', 'Price', 'Units', 'Allocated Capital', 'Current P&L ($)', 'Return %', 'Hard Stop-Loss Price']],
                column_config={
                    "Entry Price": st.column_config.NumberColumn("Simulated Entry", format="$%.2f"),
                    "Price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                    "Allocated Capital": st.column_config.NumberColumn("Position Value", format="$%.2f"),
                    "Current P&L ($)": st.column_config.NumberColumn("P&L ($)", format="$%.2f"),
                    "Return %": st.column_config.NumberColumn("Return", format="%.2f%%"),
                    "Hard Stop-Loss Price": st.column_config.NumberColumn("Stop Level", format="$%.2f")
                }, disabled=True, hide_index=True, use_container_width=True
            )
        else: st.warning("No stocks currently match execution filter profiles.")
    else: st.error("⚠️ Data pipeline offline.")

elif app_mode == "Global Macro Forex Router":
    st.header("🏦 Institutional Global Macro Currency Router")
    st.markdown("Macro tracking architecture for evaluating key interest yield parameters.")
    rates_data = {
        "Country": ["United States (USD)", "Australia (AUD)", "Eurozone (EUR)", "United Kingdom (GBP)", "Canada (CAD)", "Japan (JPY)"],
        "Central Bank Rate": [5.25, 4.35, 4.00, 5.00, 4.50, 0.25],
        "Inflation Rate %": [2.6, 3.4, 2.2, 2.0, 2.5, 2.1]
    }
    rates_df = pd.DataFrame(rates_data)

    c1, c2 = st.columns([1, 2])
    with c1:
        st.subheader("📌 Global Benchmark Yield Matrix")
        st.dataframe(rates_df, hide_index=True, use_container_width=True)
    
    with c2:
        st.subheader("📈 Intermarket Sentiment Data Engines")
        try:
            forex_proxies = Ticker(["CL=F", "GC=F", "^VIX"]).history(period="5d")
            oil_last = float(forex_proxies.loc["CL=F"]['adjclose'].iloc[-1])
            oil_prev = float(forex_proxies.loc["CL=F"]['adjclose'].iloc[-2])
            oil_change = ((oil_last - oil_prev) / oil_prev) * 100
            gold_last = float(forex_proxies.loc["GC=F"]['adjclose'].iloc[-1])
            gold_prev = float(forex_proxies.loc["GC=F"]['adjclose'].iloc[-2])
            gold_change = ((gold_last - gold_prev) / gold_prev) * 100
            vix_last = float(forex_proxies.loc["^VIX"]['adjclose'].iloc[-1])
        except Exception:
            oil_last, oil_change, gold_last, gold_change, vix_last = 75.0, 0.0, 2300.0, 0.0, 14.5

        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Crude Oil (CAD Link)", f"${oil_last:.2f} bbl", f"{oil_change:+.2f}%")
        mc2.metric("Gold Futures (Safe Haven)", f"${gold_last:.2f} oz", f"{gold_change:+.2f}%")
        risk_state = "🟢 Risk-On" if vix_last < 20 else "🚨 Risk-Off"
        mc3.metric("CBOE VIX (Global Risk)", f"{vix_last:.2f} pts", risk_state)

    st.markdown("---")
    st.subheader("🧠 Algorithmic Institutional Structural Bias Engine")
    aud_usd_yield_diff = 4.35 - 5.25
    aud_jpy_yield_diff = 4.35 - 0.25

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("### 🇦🇺 AUD/USD Structural Outlook")
        st.write(f"**Yield Differential:** `{aud_usd_yield_diff:.2f}%`")
        if vix_last > 20: st.error("🚨 **BIAS: SAFE HAVEN DEFENSIVE FLIGHT**")
        else: st.success("⚡ **BIAS: SPECULATIVE REGIME ACTIVE**")

    with col_b2:
        st.markdown("### 💴 AUD/JPY Institutional Carry Tracker")
        st.write(f"**Yield Differential:** `{aud_jpy_yield_diff:+.2f}%`")
        if vix_last < 18: st.success("💰 **BIAS: ACTIVE CARRY DEPLOYMENT**")
        else: st.error("💥 **BIAS: CARRY UNWINDING DANGER**")

elif app_mode == "Trend Momentum Screener":
    st.header("🟢 Original Elite Momentum Screener (ASX 50)")
    with st.spinner("Processing trend filters..."):
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
                "Distance to Peak ($)": st.column_config.NumberColumn(format="$%.2f")
            }, disabled=True, hide_index=True, use_container_width=True
        )
    else: st.error("⚠️ Pipeline failure.")

elif app_mode == "Fundamental Value Searcher":
    st.header("💎 Fundamental Balance Sheet Matrix")
    with st.spinner("Extracting reports..."):
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
            }, disabled=True, hide_index=True, use_container_width=True
        )
    else: st.error("⚠️ Connection error.")

elif app_mode == "WD Gann Mechanical Screener":
    st.header("🦅 Advanced WD Gann Structural Matrix")
    gann_filter = st.radio("Isolate Swing Layers", ["All Matrix Assets", "Up-Swings Only", "Volatility Breaks"], horizontal=True)
    with st.spinner("Calculating geometric pivots..."):
        data_pool = fetch_master_dataset_pool(ASX_50)
    if data_pool:
        res_df = pd.DataFrame(data_pool)
        if gann_filter == "Up-Swings Only": res_df = res_df[res_df["Gann Signal"].str.contains("UP-SWING")]
        elif gann_filter == "Volatility Breaks": res_df = res_df[res_df["Current Candle Type"].str.contains("Outside")]
        st.data_editor(
            res_df[['Name', 'Chart Link', 'Gann Signal', 'Current Candle Type', 'Price', 'Dist 52W High %']],
            column_config={
                "Chart Link": st.column_config.LinkColumn("Open Workspace", display_text="📈 Launch TV Chart"),
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Dist 52W High %": st.column_config.NumberColumn(format="%.2f%%")
            }, disabled=True, hide_index=True, use_container_width=True
        )
    else: st.error("⚠️ Data error.")

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
    else: st.warning("Could not pull real-time API metrics, loading live chart view...")

    tradingview_html = f"""
    <div class="tradingview-widget-container" style="height:550px; width:100%;"><div id="tradingview_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "ASX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tradingview_chart"}});
      </script>
    </div>
    """
    components.html(tradingview_html, height=570)
