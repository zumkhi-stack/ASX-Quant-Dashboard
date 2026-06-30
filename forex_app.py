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
    st.header("⚙️ Institutional Manual Execution Terminal")
    st.caption("Review algorithmic entry/exit signals below and lock positions into your portfolio manually to track them accurately.")

    # 1. Initialize Virtual Core Account Balance & Ledger History in Memory
    if "fx_account" not in st.session_state:
        st.session_state.fx_account = {
            "cash": 50000.00,        # Initial Sandbox Balance ($ AUD)
            "positions": {},         # Stores permanently locked open pairs
            "ledger": []             # Stores closed trades history list
        }

    # 2. Strategy Tuning Controls
    st.sidebar.subheader("⚙️ Automated Rule Configurations")
    risk_pct = st.sidebar.slider("Execution Trailing Risk Stop %", 0.5, 5.0, 1.5, step=0.1)
    trade_size = st.sidebar.number_input("Fixed Size Per Trade ($ Base Units)", value=10000, step=1000)

    # Reset Portfolio Button
    if st.sidebar.button("Wipe Sandbox & Reset Cash"):
        st.session_state.fx_account = {"cash": 50000.00, "positions": {}, "ledger": []}
        st.rerun()

    # 3. Pull Current Live Engine Signal Structures
    with st.spinner("Processing live signals..."): 
        data_pool = fetch_forex_dataset_pool(FOREX_MAJORS)

    if data_pool:
        current_market = {item["Name"]: item for item in data_pool}
        
        # --- NEW VISUAL SIGNAL MATRIX ---
        st.subheader("📡 Live Strategy Signal Feed")
        signal_rows = []
        for name, asset in current_market.items():
            gann_up = "GANN UP" in asset["Gann Signal"]
            is_bullish = asset["is_bullish"]
            
            # Check status
            if name in st.session_state.fx_account["positions"]:
                status = "💼 Already in Portfolio"
            elif is_bullish and gann_up:
                status = "🟢 BUY SIGNAL GENERATED"
            else:
                status = "⚪ Scanning / Neutral"
                
            signal_rows.append({
                "Asset Pair": name,
                "Current Rate": f"{asset['Price']:.4f}",
                "Gann Direction": asset["Gann Signal"],
                "Trend Structure": "🚀 BULLISH" if is_bullish else "⚠️ BEARISH",
                "System Action Alert": status
            })
        st.dataframe(pd.DataFrame(signal_rows), hide_index=True, use_container_width=True)

        # --- PORTFOLIO ORDER SUBMISSION INTERFACES ---
        st.markdown("---")
        st.subheader("🕹️ Order Execution Pad")
        
        # Filter down pairs that have an active buy signal and aren't owned yet
        available_buys = [r["Asset Pair"] for r in signal_rows if "BUY SIGNAL" in r["System Action Alert"]]
        
        col_exec1, col_exec2 = st.columns(2)
        
        with col_exec1:
            if available_buys:
                selected_buy = st.selectbox("Select Active Signal Pair to Buy", available_buys)
                if st.button(f"🚀 Execute Market BUY Order: {selected_buy}"):
                    if st.session_state.fx_account["cash"] >= trade_size:
                        price_now = current_market[selected_buy]["Price"]
                        st.session_state.fx_account["cash"] -= trade_size
                        # Lock it into memory permanently
                        st.session_state.fx_account["positions"][selected_buy] = {
                            "entry": price_now,
                            "size": trade_size,
                            "stop_loss": price_now * (1 - (risk_pct / 100)),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        st.toast(f"Locked {selected_buy} into portfolio!")
                        st.rerun()
                    else:
                        st.error("Insufficient Cash Pool.")
            else:
                st.info("No active structural buy alerts ready for deployment right now.")

        with col_exec2:
            active_owned = list(st.session_state.fx_account["positions"].keys())
            if active_owned:
                selected_exit = st.selectbox("Select Active Position to Liquidate", active_owned)
                if st.button(f"🚨 Execute Market SELL Order: {selected_exit}"):
                    pos = st.session_state.fx_account["positions"][selected_exit]
                    price_now = current_market[selected_exit]["Price"]
                    
                    return_multiplier = price_now / pos["entry"]
                    liquidated_cash = pos["size"] * return_multiplier
                    pnl_pct = ((price_now - pos["entry"]) / pos["entry"]) * 100
                    pnl_cash = (pos["size"] / pos["entry"]) * (price_now - pos["entry"])
                    
                    st.session_state.fx_account["ledger"].append({
                        "Asset Pair": selected_exit, "Entry Time": pos["timestamp"], "Exit Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Entry Rate": f"{pos['entry']:.4f}", "Exit Rate": f"{price_now:.4f}", "Reason": "🎯 MANUAL TARGET EXIT",
                        "Return %": f"{pnl_pct:+.2f}%", "Final P&L ($)": f"${pnl_cash:+.2f}"
                    })
                    st.session_state.fx_account["cash"] += liquidated_cash
                    del st.session_state.fx_account["positions"][selected_exit]
                    st.toast(f"Successfully Sold {selected_exit}!")
                    st.rerun()
            else:
                st.info("No active open trades to close manually.")

        # --- BACKGROUND PROTECTION AUTOMATION (Stop Loss Tracker) ---
        for name in list(st.session_state.fx_account["positions"].keys()):
            pos = st.session_state.fx_account["positions"][name]
            price = current_market[name]["Price"]
            
            if price <= pos["stop_loss"]:
                return_multiplier = price / pos["entry"]
                liquidated_cash = pos["size"] * return_multiplier
                pnl_pct = ((price - pos["entry"]) / pos["entry"]) * 100
                pnl_cash = (pos["size"] / pos["entry"]) * (price - pos["entry"])
                
                st.session_state.fx_account["ledger"].append({
                    "Asset Pair": name, "Entry Time": pos["timestamp"], "Exit Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Entry Rate": f"{pos['entry']:.4f}", "Exit Rate": f"{price:.4f}", "Reason": "🛑 STOP LOSS TRIGGERED",
                    "Return %": f"{pnl_pct:+.2f}%", "Final P&L ($)": f"${pnl_cash:+.2f}"
                })
                st.session_state.fx_account["cash"] += liquidated_cash
                del st.session_state.fx_account["positions"][name]
                st.toast(f"CRITICAL RISK ACTION: {name} hit hard Stop Loss limit.")
                st.rerun()

        # 4. LIVE ACCOUNT DASHBOARD METRICS DISPLAY
        open_positions = st.session_state.fx_account["positions"]
        current_floating_value = 0.0
        active_rows = []
        
        for name, pos in open_positions.items():
            curr_price = current_market[name]["Price"]
            pnl_pct = ((curr_price - pos["entry"]) / pos["entry"]) * 100
            pnl_cash = (pos["size"] / pos["entry"]) * (curr_price - pos["entry"])
            current_floating_value += (pos["size"] + pnl_cash)
            
            active_rows.append({
                "Asset Pair": name, "Execution Time": pos["timestamp"], "Entry Rate": f"{pos['entry']:.4f}",
                "Current Rate": f"{curr_price:.4f}", "Stop Level": f"{pos['stop_loss']:.4f}",
                "Return Status": f"{pnl_pct:+.2f}%", "Floating P&L ($)": f"${pnl_cash:+.2f}"
            })

        total_equity = st.session_state.fx_account["cash"] + current_floating_value
        total_pnl = total_equity - 50000.00

        st.markdown("---")
        st.subheader("📋 Core Live Open Portfolio Account Status")
        m1, m2, m3 = st.columns(3)
        m1.metric("Available Balance Cash", f"${st.session_state.fx_account['cash']:,.2f} AUD")
        m2.metric("Total Net Portfolio Equity", f"${total_equity:,.2f} AUD")
        m3.metric("Net Total Realized Returns", f"${total_pnl:,.2f} AUD", delta=f"{total_pnl:+.2f}")

        if active_rows:
            st.dataframe(pd.DataFrame(active_rows), hide_index=True, use_container_width=True)
        else:
            st.info("Your portfolio is currently empty. Use the order pad above to execute active signals.")

        # 5. HISTORICAL RECORDS LEDGER
        st.markdown("---")
        st.subheader("📚 Historical Closed Ledger (Real-Time Performance Track)")
        if st.session_state.fx_account["ledger"]:
            ledger_df = pd.DataFrame(st.session_state.fx_account["ledger"])
            st.dataframe(ledger_df.iloc[::-1], hide_index=True, use_container_width=True)
        else:
            st.info("No closed trades archived yet for this session.")

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
