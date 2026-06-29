import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components
from datetime import datetime

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ASX Master Quant Command Center", layout="wide")
st.title("📊 ASX Master Quantitative & Geometric Command Center")

# 🚨 REPLACE THIS WITH YOUR UNIQUE PUBLISHED GOOGLE SHEET CSV LINK
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRptWADWEtvCYG8XCsJYJvCB29DacMP-HbvjU99z9unr-DMOnLhac38G7ParfiVmBvs-v_hAY1jH109/pub?gid=0&single=true&output=csv"

# --- CORE TARGET LIST ---
ASX_CORE = ["BHP", "CBA", "WBC", "NAB", "ANZ"]

# --- SIDEBAR MATRICES & DYNAMIC SEARCH ---
st.sidebar.header("🔍 Global Market Router")
raw_search = st.sidebar.text_input("Deep Research Search (e.g. PLS, REA)", "").strip().upper()

st.sidebar.markdown("---")
st.sidebar.header("🎯 Navigation Matrix")
app_mode = st.sidebar.selectbox("Choose App Workspace", [
    "Automated Quant Fund Simulator",  
    "Global Macro Forex Router",       
    "Trend Momentum Screener",
    "Fundamental Value Searcher",
    "WD Gann Mechanical Screener",
    "Interactive Charting Workspace"
])

if raw_search:
    clean_symbol = raw_search.split('.')[0]
    if app_mode not in ["Trend Momentum Screener", "WD Gann Mechanical Screener", "Automated Quant Fund Simulator"]:
        app_mode = "Interactive Charting Workspace"
else:
    if app_mode == "Interactive Charting Workspace":
        ticker_choice = st.sidebar.selectbox("Select Core Portfolio Ticker", ASX_CORE)
        clean_symbol = ticker_choice
    else:
        clean_symbol = "BHP"

tv_direct_url = f"https://www.tradingview.com/chart/?symbol=ASX%3A{clean_symbol}"
st.sidebar.markdown("---")
st.sidebar.header("🚀 Personal Pine Scripts Gateway")
st.sidebar.link_button(f"🔓 Open {clean_symbol} Workspace", tv_direct_url, type="primary", use_container_width=True)

# --- RESTORED MASTER QUANT PIPELINE ENGINE ---
@st.cache_data(ttl=60)
def fetch_restored_quant_dataset(url):
    compiled_results = []
    try:
        # Import clean unthrottled historical rows directly from Google Sheet
        master_df = pd.read_csv(url)
        
        # Google Finance data columns: Date, Open, High, Low, Close, Volume
        master_df['Date'] = pd.to_datetime(master_df['Date'], errors='coerce')
        master_df = master_df.dropna(subset=['Date'])
        
        # Map out historical tables manually for each asset
        # Because we merged tables in Google Sheets, we track rows using data blocks
        total_rows = len(master_df)
        chunk_size = total_rows // len(ASX_CORE)
        
        for idx, ticker in enumerate(ASX_CORE):
            start_row = idx * chunk_size
            end_row = start_row + chunk_size if idx < len(ASX_CORE)-1 else total_rows
            
            df = master_df.iloc[start_row:end_row].copy().reset_index(drop=True)
            if df.empty or len(df) < 50: continue
            
            # Rebuilding original quantitative math
            df['50_MA'] = df['Close'].rolling(window=50).mean()
            df['200_MA'] = df['Close'].rolling(window=200).mean()
            
            latest_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2]) if len(df) > 1 else latest_close
            high_52w = float(df['High'].max())
            dist_to_high = ((high_52w - latest_close) / high_52w) * 100
            distance_usd = high_52w - latest_close
            is_bullish_trend = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1])

            # Rebuilding Candlestick Structural Breakouts
            h, l = float(df['High'].iloc[-1]), float(df['Low'].iloc[-1])
            ph, pl = float(df['High'].iloc[-2]), float(df['Low'].iloc[-2])

            if h > ph and l < pl: bar_type = "🟠 Outside Bar (Volatility)"
            elif h <= ph and l >= pl: bar_type = "⚪ Inside Bar (Consolidation)"
            elif h > ph and l >= pl: bar_type = "🟢 Up Bar (Bullish)"
            else: bar_type = "🔴 Down Bar (Bearish)"

            # Rebuilding original WD Gann Mechanical Swing Engine
            swing_dir = 1
            for i in range(2, len(df)):
                if float(df['High'].iloc[i]) > float(df['High'].iloc[i-2]) and swing_dir == -1: swing_dir = 1
                elif float(df['Low'].iloc[i]) < float(df['Low'].iloc[i-2]) and swing_dir == 1: swing_dir = -1

            gann_signal = "🟢 GANN UP-SWING" if swing_dir == 1 else "🚨 GANN DOWN-SWING"

            compiled_results.append({
                "Ticker": f"{ticker}.AX", "Name": ticker, "Entry Price": prev_close, "Price": latest_close, 
                "Dist 52W High %": dist_to_high, "Distance to Peak ($)": distance_usd, "is_bullish": is_bullish_trend,
                "Gann Signal": gann_signal, "Current Candle Type": bar_type
            })
        return compiled_results
    except Exception as e:
        return []

# --- EXECUTING WORKSPACE ROUTER CHANNELS ---

with st.spinner("Processing restored indicators over secure unthrottled channels..."):
    data_pool = fetch_restored_quant_dataset(SHEET_URL)

if not data_pool:
    st.error("🚨 Cloud Connection Pending. Check that your Google Sheet URL is published completely to CSV.")
    st.stop()

res_df = pd.DataFrame(data_pool)

if app_mode == "Automated Quant Fund Simulator":
    st.header("🤖 Automated Quant Management Simulator (Top Allocation Loop)")
    st.sidebar.subheader("⚙️ Quant System Tuning")
    max_risk = st.sidebar.slider("Maximum Trailing Stop-Loss %", 3.0, 15.0, 7.5, step=0.5)
    allocation_pool = st.sidebar.number_input("Total Sandbox Capital ($ AUD)", value=20000, step=1000)

    quant_targets = res_df[(res_df["is_bullish"] == True) & (res_df["Gann Signal"].str.contains("UP-SWING"))].copy()
    quant_targets = quant_targets.sort_values(by="Dist 52W High %", ascending=True)
    top_5_portfolio = quant_targets.head(5).copy()
    
    if not top_5_portfolio.empty:
        per_stock_cash = allocation_pool / len(top_5_portfolio)
        top_5_portfolio["Allocated Capital"] = per_stock_cash
        top_5_portfolio["Units"] = (per_stock_cash / top_5_portfolio["Entry Price"]).astype(int)
        top_5_portfolio["Hard Stop-Loss Price"] = top_5_portfolio["Entry Price"] * (1 - (max_risk / 100))
        top_5_portfolio["Return %"] = ((top_5_portfolio["Price"] - top_5_portfolio["Entry Price"]) / top_5_portfolio["Entry Price"]) * 100
        top_5_portfolio["Current P&L ($)"] = top_5_portfolio["Units"] * (top_5_portfolio["Price"] - top_5_portfolio["Entry Price"])
        
        total_pnl = top_5_portfolio["Current P&L ($)"].sum()
        total_return = (total_pnl / allocation_pool) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Capital Slots Used", f"{len(top_5_portfolio)} Loaded")
        m2.metric("Sizing Weight Per Asset", f"${per_stock_cash:,.2f} AUD")
        if total_pnl >= 0: m3.metric("Total Fund P&L", f"+${total_pnl:,.2f} AUD", f"🟢 +{total_return:.2f}%")
        else: m3.metric("Total Fund P&L", f"-${abs(total_pnl):,.2f} AUD", f"🔴 {total_return:.2f}%")

        st.subheader("💼 Active System Portfolios (Real-Time Performance Tracking)")
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
    else:
        st.warning("No assets currently match both Bullish 50/200MA trend metrics and Gann Up-Swing confirmations.")

elif app_mode == "Trend Momentum Screener":
    st.header("🟢 Original Elite Momentum Screener")
    filtered = res_df[(res_df["is_bullish"] == True) & (res_df["Dist 52W High %"] <= 25.0)].copy()
    st.data_editor(
        filtered[['Name', 'Price', 'Dist 52W High %', 'Distance to Peak ($)']],
        column_config={
            "Price": st.column_config.NumberColumn(format="$%.2f"),
            "Dist 52W High %": st.column_config.NumberColumn(format="%.2f%%"),
            "Distance to Peak ($)": st.column_config.NumberColumn(format="$%.2f")
        }, disabled=True, hide_index=True, use_container_width=True
    )

elif app_mode == "WD Gann Mechanical Screener":
    st.header("🦅 Advanced WD Gann Structural Matrix")
    st.data_editor(
        res_df[['Name', 'Gann Signal', 'Current Candle Type', 'Price']],
        column_config={"Price": st.column_config.NumberColumn(format="$%.2f")},
        disabled=True, hide_index=True, use_container_width=True
    )

elif app_mode == "Global Macro Forex Router":
    st.header("🏦 Institutional Global Macro Currency Router")
    rates_data = {"Country": ["United States (USD)", "Australia (AUD)", "Japan (JPY)"], "Central Bank Rate": [5.25, 4.35, 0.25]}
    st.dataframe(pd.DataFrame(rates_data), hide_index=True, use_container_width=True)
    st.success("💰 **FOREX MATRIX ROUTING CHANNELS READY**")

elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Deep Research Terminal: ASX:{clean_symbol}")
    tradingview_html = f"""
    <div style="height:550px; width:100%;"><div id="tv" style="height:100%; width:100%;"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>new TradingView.widget({{"autosize": true, "symbol": "ASX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tv"}});</script>
    </div>
    """
    components.html(tradingview_html, height=570)
