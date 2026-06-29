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
    asset_type_label = "Stock"
elif market_tier == "Global Macro Forex Pairs":
    active_universe = FOREX_MAJORS
    asset_type_label = "Currency Pair"
else:
    active_universe = ASX_50 + FOREX_MAJORS
    asset_type_label = "Asset"

st.sidebar.markdown("---")
st.sidebar.header("🔍 Global Market Router")
raw_search = st.sidebar.text_input("Deep Research Search (e.g. PLS, REA, AUDUSD)", "").strip().upper()

st.sidebar.markdown("---")
st.sidebar.header("🎯 Navigation Matrix")
app_mode = st.sidebar.selectbox("Choose App Workspace", [
    "Automated Quant Fund Simulator",  
    "Global Macro Forex Router",       
    "Trend Momentum Screener",
    "WD Gann Mechanical Screener",
    "Interactive Charting Workspace"
])

# Search normalization filter logic
if raw_search:
    if any(fx in raw_search for fx in ["USD", "JPY", "EUR", "GBP", "AUD", "NZD"]):
        target_ticker = f"{raw_search}=X" if not raw_search.endswith("=X") else raw_search
        clean_symbol = raw_search.replace("=X", "")
    else:
        target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
        clean_symbol = raw_search.split('.')[0]
    
    if app_mode not in ["Global Macro Forex Router", "Trend Momentum Screener", "WD Gann Mechanical Screener", "Automated Quant Fund Simulator"]:
        app_mode = "Interactive Charting Workspace"
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
        if history is None or (isinstance(history, dict) and not history): return []
    except Exception:
        return []

    for ticker in ticker_list:
        try:
            if isinstance(history.index, pd.MultiIndex):
                if ticker not in history.index.levels[0]: continue
                df = history.loc[ticker].dropna().copy()
            else:
                df = history.dropna().copy()

            if df.empty or len(df) < 50: continue

            # Apply standard algorithmic overlays across all assets
            df['50_MA'] = df['adjclose'].rolling(window=50).mean()
            df['200_MA'] = df['adjclose'].rolling(window=200).mean()
            latest_close = float(df['adjclose'].iloc[-1])
            prev_close = float(df['adjclose'].iloc[-2]) if len(df) > 1 else latest_close
            high_52w = float(df['high'].max())
            dist_to_high = ((high_52w - latest_close) / high_52w) * 100
            is_bullish_trend = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1])

            # Candle pattern evaluation
            df['prev_high'] = df['high'].shift(1)
            df['prev_low'] = df['low'].shift(1)
            last_row = df.iloc[-1]
            h, l, ph, pl = last_row['high'], last_row['low'], last_row['prev_high'], last_row['prev_low']

            if h > ph and l < pl: bar_type = "🟠 Outside Bar"
            elif h <= ph and l >= pl: bar_type = "⚪ Inside Bar"
            elif h > ph and l >= pl: bar_type = "🟢 Up Bar"
            else: bar_type = "🔴 Down Bar"

            # WD Gann Mechanical Swing Framework
            swing_dir = 1
            for i in range(2, len(df)):
                if df['high'].iloc[i] > df['high'].iloc[i-2] and swing_dir == -1: swing_dir = 1
                elif df['low'].iloc[i] < df['low'].iloc[i-2] and swing_dir == 1: swing_dir = -1

            gann_signal = "🟢 GANN UP-SWING" if swing_dir == 1 else "🚨 GANN DOWN-SWING"
            
            raw_name = ticker.replace(".AX", "").replace("=X", "")
            tv_prefix = "" if "=X" in ticker else "ASX:"
            link_url = f"https://www.tradingview.com/chart/?symbol={tv_prefix}{raw_name}"

            compiled_results.append({
                "Ticker": ticker, "Chart Link": link_url, "Name": raw_name, "Entry Price": prev_close, "Price": latest_close, 
                "Dist 52W High %": dist_to_high, "is_bullish": is_bullish_trend, "Gann Signal": gann_signal, "Current Candle Type": bar_type
            })
        except Exception: continue
    return compiled_results

# --- EXECUTE APP WINDOW CHANNELS ---

if app_mode == "Automated Quant Fund Simulator":
    st.header(f"🤖 Multi-Asset Quant Management Simulator ({market_tier})")
    st.markdown("Maintains a rigorous, objective allocation framework based entirely on mathematical trend and geometric models.")

    st.sidebar.subheader("⚙️ Quant System Tuning")
    max_risk = st.sidebar.slider("Maximum Trailing Stop-Loss %", 1.0, 15.0, 5.0, step=0.5)
    allocation_pool = st.sidebar.number_input("Total Sandbox Capital ($ AUD)", value=20000, step=1000)

    with st.spinner("Analyzing cross-market technical frameworks..."):
        data_pool = fetch_master_dataset_pool(active_universe)

    if data_pool:
        res_df = pd.DataFrame(data_pool)
        quant_targets = res_df[(res_df["is_bullish"] == True) & (res_df["Gann Signal"].str.contains("UP-SWING"))].copy()
        quant_targets = quant_targets.sort_values(by="Dist 52W High %", ascending=True)
        top_5_portfolio = quant_targets.head(5).copy()
        
        if not top_5_portfolio.empty:
            per_asset_cash = allocation_pool / len(top_5_portfolio)
            top_5_portfolio["Allocated Capital"] = per_asset_cash
            top_5_portfolio["Hard Stop-Loss Level"] = top_5_portfolio["Entry Price"] * (1 - (max_risk / 100))
            top_5_portfolio["Return %"] = ((top_5_portfolio["Price"] - top_5_portfolio["Entry Price"]) / top_5_portfolio["Entry Price"]) * 100
            top_5_portfolio["Current P&L ($)"] = (per_asset_cash / top_5_portfolio["Entry Price"]) * (top_5_portfolio["Price"] - top_5_portfolio["Entry Price"])
            
            total_pnl = top_5_portfolio["Current P&L ($)"].sum()
            total_return = (total_pnl / allocation_pool) * 100
            
            m1, m2, m3 = st.columns(3)
            m1.metric("Active Allocations Loaded", f"{len(top_5_portfolio)} Selected")
            m2.metric("Sizing Symmetrical Weight", f"${per_asset_cash:,.2f} AUD")
            if total_pnl >= 0: m3.metric("Total Strategic P&L", f"+${total_pnl:,.2f} AUD", f"🟢 +{total_return:.2f}%")
            else: m3.metric("Total Strategic P&L", f"-${abs(total_pnl):,.2f} AUD", f"🔴 {total_return:.2f}%")

            st.subheader("💼 Active Strategy Tracking Model")
            st.data_editor(
                top_5_portfolio[['Name', 'Entry Price', 'Price', 'Allocated Capital', 'Current P&L ($)', 'Return %', 'Hard Stop-Loss Level']],
                column_config={
                    "Entry Price": st.column_config.NumberColumn("Baseline Level", format="%.4f"),
                    "Price": st.column_config.NumberColumn("Current Close", format="%.4f"),
                    "Allocated Capital": st.column_config.NumberColumn("Risk Sizing Value", format="$%.2f"),
                    "Current P&L ($)": st.column_config.NumberColumn("P&L ($)", format="$%.2f"),
                    "Return %": st.column_config.NumberColumn("Return", format="%.2f%%"),
                    "Hard Stop-Loss Level": st.column_config.NumberColumn("Stop Loss Pivot", format="%.4f")
                }, disabled=True, hide_index=True, use_container_width=True
            )
        else: st.warning("No assets across the active profile currently meet criteria.")
    else: st.error("⚠️ Data connection offline.")

elif app_mode == "Global Macro Forex Router":
    st.header("🏦 Institutional Global Macro Currency Router")
    rates_data = {
        "Country": ["United States (USD)", "Australia (AUD)", "Eurozone (EUR)", "United Kingdom (GBP)", "Japan (JPY)"],
        "Central Bank Rate": [5.25, 4.35, 4.00, 5.00, 0.25],
        "Inflation Rate %": [2.6, 3.4, 2.2, 2.0, 2.1]
    }
    st.dataframe(pd.DataFrame(rates_data), hide_index=True, use_container_width=True)

elif app_mode == "Trend Momentum Screener":
    st.header(f"🟢 Original Elite Momentum Screener ({market_tier})")
    with st.spinner("Processing filters..."):
        data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        res_df = pd.DataFrame(data_pool)
        filtered = res_df[(res_df["is_bullish"] == True)].copy().sort_values(by="Dist 52W High %")
        st.data_editor(
            filtered[['Name', 'Chart Link', 'Price', 'Dist 52W High %']],
            column_config={
                "Chart Link": st.column_config.LinkColumn("Open Workspace", display_text="📈 Open Widget Chart"),
                "Price": st.column_config.NumberColumn(format="%.4f"),
                "Dist 52W High %": st.column_config.NumberColumn(format="%.2f%%")
            }, disabled=True, hide_index=True, use_container_width=True
        )

elif app_mode == "WD Gann Mechanical Screener":
    st.header("🦅 Advanced WD Gann Structural Matrix")
    with st.spinner("Mapping geometric channels..."):
        data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        res_df = pd.DataFrame(data_pool)
        st.data_editor(
            res_df[['Name', 'Chart Link', 'Gann Signal', 'Current Candle Type', 'Price']],
            column_config={
                "Chart Link": st.column_config.LinkColumn("Open Workspace", display_text="📈 Open Widget Chart"),
                "Price": st.column_config.NumberColumn(format="%.4f")
            }, disabled=True, hide_index=True, use_container_width=True
        )

elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Deep Research Terminal: {clean_symbol}")
    
    tv_symbol = f"FX:{clean_symbol}" if any(fx in clean_symbol for fx in ["USD", "JPY", "EUR", "GBP", "AUD", "NZD"]) else f"ASX:{clean_symbol}"
    
    tradingview_html = f"""
    <div style="height:550px; width:100%;"><div id="tradingview_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">
      new TradingView.widget({{"autosize": true, "symbol": "{tv_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tradingview_chart"}});
      </script>
    </div>
    """
    components.html(tradingview_html, height=570)
