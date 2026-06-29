import streamlit as st
import pandas as pd
import numpy as np
import streamlit.components.v1 as components

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ASX Master Quant Command Center", layout="wide")
st.title("📊 ASX Master Quantitative & Geometric Command Center")

# 🚨 REPLACE THIS WITH YOUR ACTUALLY PUBLISHED GOOGLE SHEET CSV LINK
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRptWADWEtvCYG8XCsJYJvCB29DacMP-HbvjU99z9unr-DMOnLhac38G7ParfiVmBvs-v_hAY1jH109/pub?gid=0&single=true&output=csv"

# --- CORE DATA TIERS ---
ASX_CORE = ["BHP", "CBA", "WBC", "NAB", "ANZ"]

# --- SIDEBAR MATRICES & DYNAMIC SEARCH ---
st.sidebar.header("🔍 Global Market Router")
raw_search = st.sidebar.text_input("Deep Research Search (e.g. PLS, REA)", "").strip().upper()

st.sidebar.markdown("---")
st.sidebar.header("🎯 Navigation Matrix")
app_mode = st.sidebar.selectbox("Choose App Workspace", [
    "Automated Quant Fund Simulator",  
    "Global Macro Forex Router",       
    "Interactive Charting Workspace"
])

if raw_search:
    clean_symbol = raw_search.split('.')[0]
    if app_mode not in ["Automated Quant Fund Simulator", "Global Macro Forex Router"]:
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

# --- UNLIMITED DATA PIPELINE VIA GOOGLE SHEETS ---
@st.cache_data(ttl=60)  # Rechecks Google Sheet every 60 seconds
def fetch_unlimited_market_data(url):
    try:
        # Pull the live published spreadsheet data instantly
        df = pd.read_csv(url)
        compiled_results = []
        
        for idx, row in df.iterrows():
            ticker = str(row['Ticker'])
            price = float(row['Price'])
            entry = float(row['Prev_Close'])
            
            # Simple Trend Evaluator (Using Entry vs Close variations as mock indicators)
            is_bullish_trend = price >= entry
            gann_signal = "🟢 GANN UP-SWING" if price > entry else "🚨 GANN DOWN-SWING"
            bar_type = "🟢 Up Bar (Bullish)" if price > entry else "🔴 Down Bar (Bearish)"
            
            compiled_results.append({
                "Name": ticker, 
                "Entry Price": entry, 
                "Price": price, 
                "is_bullish": is_bullish_trend,
                "Gann Signal": gann_signal, 
                "Current Candle Type": bar_type
            })
        return compiled_results
    except Exception as e:
        st.error(f"Sheet Link Inactive. Please check your SHEET_URL configurations. Error: {e}")
        return []

# --- APP WORKSPACE ROUTING CHANNELS ---

if app_mode == "Automated Quant Fund Simulator":
    st.header("🤖 Automated Quant Management Simulator (Unthrottled Sheet Feed)")
    st.markdown("This workspace runs securely on decentralized cloud channels via Google Finance endpoints.")

    st.sidebar.subheader("⚙️ Quant System Tuning")
    max_risk = st.sidebar.slider("Maximum Trailing Stop-Loss %", 3.0, 15.0, 7.5, step=0.5)
    allocation_pool = st.sidebar.number_input("Total Sandbox Capital ($ AUD)", value=20000, step=1000)

    # Triggering our data pull
    data_pool = fetch_unlimited_market_data(SHEET_URL)

    if data_pool:
        res_df = pd.DataFrame(data_pool)
        # Select our top trends
        top_portfolio = res_df.copy()
        
        per_stock_cash = allocation_pool / len(top_portfolio)
        top_portfolio["Allocated Capital"] = per_stock_cash
        top_portfolio["Units"] = (per_stock_cash / top_portfolio["Entry Price"]).astype(int)
        top_portfolio["Hard Stop-Loss Price"] = top_portfolio["Entry Price"] * (1 - (max_risk / 100))
        top_portfolio["Return %"] = ((top_portfolio["Price"] - top_portfolio["Entry Price"]) / top_portfolio["Entry Price"]) * 100
        top_portfolio["Current P&L ($)"] = top_portfolio["Units"] * (top_portfolio["Price"] - top_portfolio["Entry Price"])
        
        total_pnl = top_portfolio["Current P&L ($)"].sum()
        total_return = (total_pnl / allocation_pool) * 100
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Active Capital Slots Used", f"{len(top_portfolio)} / 5 Loaded")
        m2.metric("Sizing Weight Per Asset", f"${per_stock_cash:,.2f} AUD")
        if total_pnl >= 0: m3.metric("Total Fund P&L", f"+${total_pnl:,.2f} AUD", f"🟢 +{total_return:.2f}%")
        else: m3.metric("Total Fund P&L", f"-${abs(total_pnl):,.2f} AUD", f"🔴 {total_return:.2f}%")

        st.subheader("💼 Active System Portfolios (Unthrottled Stream Entries)")
        st.data_editor(
            top_portfolio[['Name', 'Entry Price', 'Price', 'Units', 'Allocated Capital', 'Current P&L ($)', 'Return %', 'Hard Stop-Loss Price']],
            column_config={
                "Entry Price": st.column_config.NumberColumn("Simulated Entry", format="$%.2f"),
                "Price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                "Allocated Capital": st.column_config.NumberColumn("Position Value", format="$%.2f"),
                "Current P&L ($)": st.column_config.NumberColumn("P&L ($)", format="$%.2f"),
                "Return %": st.column_config.NumberColumn("Return", format="%.2f%%"),
                "Hard Stop-Loss Price": st.column_config.NumberColumn("Stop Level", format="$%.2f")
            }, disabled=True, hide_index=True, use_container_width=True
        )

elif app_mode == "Global Macro Forex Router":
    st.header("🏦 Institutional Global Macro Currency Router")
    rates_data = {
        "Country": ["United States (USD)", "Australia (AUD)", "Eurozone (EUR)", "Japan (JPY)"],
        "Central Bank Rate": [5.25, 4.35, 4.00, 0.25]
    }
    st.dataframe(pd.DataFrame(rates_data), hide_index=True, use_container_width=True)
    st.success("💰 **BIAS INDICATOR: SYSTEM ACTIVE**")

elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Deep Research Terminal: ASX:{clean_symbol}")
    tradingview_html = f"""
    <div style="height:550px; width:100%;"><div id="tv" style="height:100%; width:100%;"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>new TradingView.widget({{"autosize": true, "symbol": "ASX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tv"}});</script>
    </div>
    """
    components.html(tradingview_html, height=570)
