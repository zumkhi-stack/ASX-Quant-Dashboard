import streamlit as st
import pandas as pd
import numpy as np
from alpha_vantage.timeseries import TimeSeries
import streamlit.components.v1 as components
from datetime import datetime
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ASX Master Quant Command Center", layout="wide")
st.title("📊 ASX Master Quantitative & Geometric Command Center")

# --- USER ENTERED API KEY ---
st.sidebar.header("🔑 API Authentication")
av_api_key = st.sidebar.text_input("Enter Alpha Vantage API Key", type="password", help="Get a free key from alphavantage.co")

if not av_api_key:
    st.info("💡 Please enter your free Alpha Vantage API Key in the left sidebar to unlock the cloud data pipeline.")
    st.stop()

# --- CORE DATA TIERS (Optimized for Free API Rate Limits) ---
ASX_CORE = ["BHP", "CBA", "WBC", "NAB", "ANZ"]

# --- SIDEBAR MATRICES & DYNAMIC SEARCH ---
st.sidebar.markdown("---")
st.sidebar.header("🔍 Global Market Router")
raw_search = st.sidebar.text_input("Deep Research Search (e.g. PLS, REA)", "").strip().upper()

st.sidebar.markdown("---")
st.sidebar.header("🎯 Navigation Matrix")
app_mode = st.sidebar.selectbox("Choose App Workspace", [
    "Automated Quant Fund Simulator",  
    "Global Macro Forex Router",       
    "Trend Momentum Screener",
    "Interactive Charting Workspace"
])

if raw_search:
    clean_symbol = raw_search.split('.')[0]
    if app_mode not in ["Trend Momentum Screener", "Automated Quant Fund Simulator", "Global Macro Forex Router"]:
        app_mode = "Interactive Charting Workspace"
else:
    if app_mode == "Interactive Charting Workspace":
        ticker_choice = st.sidebar.selectbox("Select Core Portfolio Ticker", ASX_CORE)
        clean_symbol = ticker_choice
    else:
        clean_symbol = "BHP"

# Set up global targets for downstream logic
target_ticker = f"ASX:{clean_symbol}"
tv_direct_url = f"https://www.tradingview.com/chart/?symbol=ASX%3A{clean_symbol}"

st.sidebar.markdown("---")
st.sidebar.header("🚀 Personal Pine Scripts Gateway")
st.sidebar.link_button(f"🔓 Open {clean_symbol} Workspace", tv_direct_url, type="primary", use_container_width=True)

# --- MASTER ALPHA VANTAGE ENGINE ---
@st.cache_data(ttl=600)  # Cached for 10 minutes to respect limits
def fetch_alpha_vantage_pool(symbol_list, api_key):
    compiled_results = []
    ts = TimeSeries(key=api_key, output_format='pandas')
    
    for symbol in symbol_list:
        try:
            # Query official US/Global Alpha Vantage standard formats 
            # Note: For ASX stocks, Alpha Vantage uses the suffix format 'BHP.AX'
            av_symbol = f"{symbol}.AX"
            data, meta = ts.get_daily(symbol=av_symbol, outputsize='compact')
            
            if data.empty: 
                continue
                
            # Rename Alpha Vantage columns to clean standard terms
            df = data.copy()
            df = df.sort_index(ascending=True) # Ensure chronological order
            df['close'] = df['4. close']
            df['high'] = df['2. high']
            df['low'] = df['3. low']
            
            # Quantitative Metrics Calculations
            df['50_MA'] = df['close'].rolling(window=50).mean()
            df['200_MA'] = df['close'].rolling(window=200).mean()
            
            latest_close = float(df['close'].iloc[-1])
            prev_close = float(df['close'].iloc[-2]) if len(df) > 1 else latest_close
            high_52w = float(df['high'].max())
            dist_to_high = ((high_52w - latest_close) / high_52w) * 100
            is_bullish_trend = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1])

            # Candlestick Architecture
            h, l = float(df['high'].iloc[-1]), float(df['low'].iloc[-1])
            ph, pl = float(df['high'].iloc[-2]), float(df['low'].iloc[-2])
            
            if h > ph and l < pl: bar_type = "🟠 Outside Bar (Volatility)"
            elif h <= ph and l >= pl: bar_type = "⚪ Inside Bar (Consolidation)"
            elif h > ph and l >= pl: bar_type = "🟢 Up Bar (Bullish)"
            else: bar_type = "🔴 Down Bar (Bearish)"

            # Gann Swing Matrix
            swing_dir = 1
            for i in range(2, len(df)):
                if float(df['high'].iloc[i]) > float(df['high'].iloc[i-2]) and swing_dir == -1: swing_dir = 1
                elif float(df['low'].iloc[i]) < float(df['low'].iloc[i-2]) and swing_dir == 1: swing_dir = -1
            gann_signal = "🟢 GANN UP-SWING" if swing_dir == 1 else "🚨 GANN DOWN-SWING"

            compiled_results.append({
                "Name": symbol, 
                "Entry Price": prev_close, 
                "Price": latest_close, 
                "Dist 52W High %": dist_to_high, 
                "is_bullish": is_bullish_trend,
                "Gann Signal": gann_signal, 
                "Current Candle Type": bar_type
            })
            
            # Pause to obey Alpha Vantage rate pacing limits
            time.sleep(1.5)
            
        except Exception as e:
            continue
            
    return compiled_results

# --- APP WORKSPACE ROUTING CHANNELS ---

if app_mode == "Automated Quant Fund Simulator":
    st.header("🤖 Automated Quant Management Simulator (Alpha Vantage Feed)")
    st.markdown("This engine processes your portfolio allocations securely using authenticated cloud data links.")

    st.sidebar.subheader("⚙️ Quant System Tuning")
    max_risk = st.sidebar.slider("Maximum Trailing Stop-Loss %", 3.0, 15.0, 7.5, step=0.5)
    allocation_pool = st.sidebar.number_input("Total Sandbox Capital ($ AUD)", value=20000, step=1000)

    with st.spinner("Accessing authenticated Alpha Vantage core streams..."):
        data_pool = fetch_alpha_vantage_pool(ASX_CORE, av_api_key)

    if data_pool:
        res_df = pd.DataFrame(data_pool)
        quant_targets = res_df[(res_df["is_bullish"] == True) & (res_df["Gann Signal"].str.contains("UP-SWING"))].copy()
        quant_targets = quant_targets.sort_values(by="Dist 52W High %", ascending=True)
        top_portfolio = quant_targets.head(5).copy()
        
        if not top_portfolio.empty:
            per_stock_cash = allocation_pool / len(top_portfolio)
            top_portfolio["Allocated Capital"] = per_stock_cash
            top_portfolio["Units"] = (per_stock_cash / top_portfolio["Entry Price"]).astype(int)
            top_portfolio["Hard Stop-Loss Price"] = top_portfolio["Entry Price"] * (1 - (max_risk / 100))
            top_portfolio["Return %"] = ((top_portfolio["Price"] - top_portfolio["Entry Price"]) / top_portfolio["Entry Price"]) * 100
            top_portfolio["Current P&L ($)"] = top_portfolio["Units"] * (top_portfolio["Price"] - top_portfolio["Entry Price"])
            
            total_pnl = top_portfolio["Current P&L ($)"].sum()
            total_return = (total_pnl / allocation_pool) * 100
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Active Capital Slots Used", f"{len(top_portfolio)} Loaded")
            m2.metric("Sizing Weight Per Asset", f"${per_stock_cash:,.2f} AUD")
            if total_pnl >= 0: m3.metric("Total Fund P&L", f"+${total_pnl:,.2f} AUD", f"🟢 +{total_return:.2f}%")
            else: m3.metric("Total Fund P&L", f"-${abs(total_pnl):,.2f} AUD", f"🔴 {total_return:.2f}%")

            st.subheader("💼 Active System Portfolios (Official Authenticated Entries)")
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
        else: st.warning("Defensive Market Context: No stocks match the Bullish Trend + Gann Upswing parameters right now.")
    else: st.error("⚠️ Alpha Vantage API Connection Failed. Verify key accuracy or check rate limits.")

elif app_mode == "Global Macro Forex Router":
    st.header("🏦 Institutional Global Macro Currency Router")
    st.markdown("Macro tracking environment for currency interest yield metrics.")
    
    rates_data = {
        "Country": ["United States (USD)", "Australia (AUD)", "Eurozone (EUR)", "Japan (JPY)"],
        "Central Bank Rate": [5.25, 4.35, 4.00, 0.25],
        "Inflation Rate %": [2.6, 3.4, 2.2, 2.1]
    }
    st.dataframe(pd.DataFrame(rates_data), hide_index=True, use_container_width=True)
    
    st.markdown("---")
    st.subheader("🧠 Algorithmic Institutional Structural Bias Engine")
    aud_usd_yield_diff = 4.35 - 5.25
    aud_jpy_yield_diff = 4.35 - 0.25

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        st.markdown("### 🇦🇺 AUD/USD Outlook")
        st.write(f"Yield Differential: `{aud_usd_yield_diff:.2f}%`")
        st.success("⚡ **BIAS: SYSTEMATIC LONG REGIME (STABLE COMMODITY CHANNELS)**")
    with col_b2:
        st.markdown("### 💴 AUD/JPY Carry Tracker")
        st.write(f"Yield Differential: `{aud_jpy_yield_diff:+.2f}%`")
        st.success("💰 **BIAS: ACTIVE CARRY DEPLOYMENT SUPPORTED**")

elif app_mode == "Trend Momentum Screener":
    st.header("🟢 Original Elite Momentum Screener")
    with st.spinner("Processing trend layers..."):
        data_pool = fetch_alpha_vantage_pool(ASX_CORE, av_api_key)
    if data_pool:
        res_df = pd.DataFrame(data_pool)
        filtered = res_df[res_df["is_bullish"] == True].copy()
        st.data_editor(
            filtered[['Name', 'Price', 'Dist 52W High %']],
            column_config={
                "Price": st.column_config.NumberColumn(format="$%.2f"),
                "Dist 52W High %": st.column_config.NumberColumn(format="%.2f%%")
            }, disabled=True, hide_index=True, use_container_width=True
        )

elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Deep Research Terminal: ASX:{clean_symbol}")
    tradingview_html = f"""
    <div style="height:550px; width:100%;"><div id="tv" style="height:100%; width:100%;"></div>
      <script src="https://s3.tradingview.com/tv.js"></script>
      <script>new TradingView.widget({{"autosize": true, "symbol": "ASX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tv"}});</script>
    </div>
    """
    components.html(tradingview_html, height=570)
