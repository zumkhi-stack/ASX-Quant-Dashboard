import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime

st.set_page_config(page_title="ASX Market Tracker Engine", layout="wide")
st.title("📊 ASX Master Quantitative Command Center")

# --- TICKER TAPE UNIVERSE INDEX ---
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{"symbols": [{"proName": "INDEX:XJO", "title": "ASX 200 Index"}, {"proName": "ASX:BHP", "title": "BHP Group"}, {"proName": "ASX:CBA", "title": "Commonwealth Bank"}, {"proName": "ASX:WBC", "title": "Westpac"}], "colorTheme": "light", "displayMode": "adaptive", "locale": "en"}
</script></div>""", height=50)

# --- UNIVERSE ARRAYS DEFINITION ---
ASX_50 = [
    "BHP.AX", "CBA.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "MQG.AX", "WES.AX", "RIO.AX", "FMG.AX", "CSL.AX",
    "WDS.AX", "TLS.AX", "TCL.AX", "WOW.AX", "QBE.AX", "GMG.AX", "MIN.AX", "APA.AX", "QAN.AX", "SPK.AX",
    "REA.AX", "ALL.AX", "SHL.AX", "COH.AX", "IPL.AX", "BSL.AX", "PPT.AX", "WHC.AX", "ALQ.AX", "LYC.AX",
    "BEN.AX", "BOQ.AX", "BLD.AX", "CAR.AX", "SGP.AX", "DXS.AX", "CHC.AX", "GPT.AX", "MGR.AX", "VCX.AX",
    "AZJ.AX", "A2M.AX", "AMP.AX", "ANN.AX", "AST.AX", "ALX.AX", "EVN.AX", "IAG.AX", "MPL.AX", "SUN.AX"
]

ASX_100_ADDITIONS = [
    "ALU.AX", "ALX.AX", "AMP.AX", "ANN.AX", "APE.AX", "ARS.AX", "AWC.AX", "BEN.AX", "BKW.AX", "BOQ.AX", 
    "BSL.AX", "BWP.AX", "BXB.AX", "CAR.AX", "CGF.AX", "CHC.AX", "CIN.AX", "CLW.AX", "CNI.AX", "COH.AX", 
    "COL.AX", "CPU.AX", "CQR.AX", "CSR.AX", "CTC.AX", "CWN.AX", "CYP.AX", "DXS.AX", "EHE.AX", "ELD.AX", 
    "FLT.AX", "FPH.AX", "GEM.AX", "GOZ.AX", "GPT.AX", "HDN.AX", "HLI.AX", "HVN.AX", "IEL.AX", "IFL.AX", 
    "IFT.AX", "ILU.AX", "IPL.AX", "JBH.AX", "JHX.AX", "LLC.AX", "LNK.AX", "LYC.AX", "MGR.AX", "MND.AX"
]

ASX_200_ADDITIONS = [
    "A2B.AX", "ABG.AX", "AFI.AX", "AGL.AX", "AIN.AX", "ALK.AX", "AMI.AX", "AMP.AX", "ANG.AX", "AO1.AX",
    "APA.AX", "APE.AX", "API.AX", "APM.AX", "APX.AX", "ARB.AX", "ARE.AX", "ARG.AX", "ARU.AX", "ASB.AX",
    "ASM.AX", "ASG.AX", "AST.AX", "ASX.AX", "AUB.AX", "AVN.AX", "AVV.AX", "AWC.AX", "AWE.AX", "AWI.AX",
    "AX1.AX", "AZS.AX", "B4P.AX", "BAB.AX", "BAL.AX", "BAP.AX", "BCB.AX", "BCI.AX", "BFL.AX", "BGA.AX",
    "BGL.AX", "BGP.AX", "BHP.AX", "BIF.AX", "BKI.AX", "BKL.AX", "BKW.AX", "BLD.AX", "BLX.AX", "BML.AX",
    "BMT.AX", "BNA.AX", "BNL.AX", "BOA.AX", "BOQ.AX", "BOT.AX", "BOU.AX", "BPT.AX", "BRG.AX", "BRL.AX",
    "BRU.AX", "BSL.AX", "BTI.AX", "BTR.AX", "BVS.AX", "BWP.AX", "BXB.AX", "C6C.AX", "CAE.AX", "CAF.AX",
    "CAJ.AX", "CAR.AX", "CBA.AX", "CCV.AX", "CDA.AX", "CDD.AX", "CDP.AX", "CE1.AX", "CEL.AX", "CEN.AX",
    "CGC.AX", "CGF.AX", "CHC.AX", "CHH.AX", "CHL.AX", "CHR.AX", "CIE.AX", "CIM.AX", "CIN.AX", "CIP.AX",
    "CKF.AX", "CLA.AX", "CLH.AX", "CLQ.AX", "CLV.AX", "CLW.AX", "CMW.AX", "CNI.AX", "CNU.AX", "COB.AX"
]

# --- SIDEBAR FILTERS ---
st.sidebar.header("🛡️ Strategy Universe Selector")
index_tier = st.sidebar.selectbox("Choose Core Index Target", ["ASX 50", "ASX 100", "ASX 200"])

# Dynamic mapping of tracking loops
# 3. Pull Current Live Engine Signal Structures Dynamically Based on Sidebar Selection
    if index_tier == "ASX 50":
        selected_universe = ASX_50
    elif index_tier == "ASX 100":
        selected_universe = ASX_50 + ASX_100_ADDITIONS
    else:
        selected_universe = ASX_50 + ASX_100_ADDITIONS + ASX_200_ADDITIONS

    with st.spinner("Processing live equity signals..."): 
        # Calls your original fetching function using the dynamic sidebar universe array
        data_pool = fetch_master_dataset_pool(selected_universe)

raw_search = st.sidebar.text_input("Stock Search (e.g. PLS, REA, BHP)", "").strip().upper()
app_mode = st.sidebar.selectbox("App Workspace", ["Automated Quant Fund Simulator", "Trend Momentum Screener", "Fundamental Value Searcher", "WD Gann Mechanical Screener", "Interactive Charting Workspace"])

if raw_search:
    target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
    clean_symbol = raw_search.split('.')[0]
else:
    target_ticker = st.sidebar.selectbox("Select Active Asset", active_universe) if app_mode == "Interactive Charting Workspace" else active_universe[0]
    clean_symbol = target_ticker.replace(".AX", "")

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
            r_name = tk.replace(".AX", "")
            l_url = f"https://www.tradingview.com/chart/?symbol=ASX:{r_name}"

            compiled_results.append({
                "Ticker": tk, "Chart Link": l_url, "Name": r_name, "Entry Price": p_prev, "Price": p_curr, 
                "Dist 52W High %": d_high, "is_bullish": is_bull, "Gann Signal": g_sig, "Current Candle Type": b_type, 
                "Trailing P/E": t_sum.get('trailingPE', np.nan),
                "Profit Margin %": t_fin.get('profitMargins', np.nan) * 100 if t_fin.get('profitMargins') else np.nan,
                "Div Yield %": t_sum.get('dividendYield', np.nan) * 100 if t_sum.get('dividendYield') else np.nan
            })
        except: continue
    return compiled_results

# --- WORKSPACES INTERFACE ROUTING ---
import json
import os

if app_mode == "Automated Quant Fund Simulator":
    st.header("⚙️ ASX Blue Chip Manual Execution Terminal (Persistent Storage)")
    st.caption("Positions are saved permanently to the database file and will survive page reloads and server restarts.")

    # --- PERMANENT STORAGE DATABASE LOGIC ---
    STOCK_DB_FILE = "stock_portfolio.json"

    def load_stock_db():
        if os.path.exists(STOCK_DB_FILE):
            try:
                with open(STOCK_DB_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {"cash": 50000.00, "positions": {}, "ledger": []}

    def save_stock_db(data):
        with open(STOCK_DB_FILE, "w") as f:
            json.dump(data, f, indent=4)

    # Load data from physical disk file into current session
    st.session_state.stock_account = load_stock_db()

    # 2. Strategy Tuning Controls
    st.sidebar.subheader("⚙️ Automated Rule Configurations")
    max_risk = st.sidebar.slider("Max Trailing Stop-Loss %", 1.0, 15.0, 5.0, step=0.5)
    trade_size = st.sidebar.number_input("Fixed Size Per Trade ($ AUD Units)", value=10000, step=1000)

    # Reset Portfolio Button
    if st.sidebar.button("Wipe Sandbox & Reset Cash"):
        if os.path.exists(STOCK_DB_FILE):
            os.remove(STOCK_DB_FILE)
        st.session_state.stock_account = {"cash": 50000.00, "positions": {}, "ledger": []}
        save_stock_db(st.session_state.stock_account)
        st.rerun()

    # 3. Pull Current Live Engine Signal Structures
    with st.spinner("Processing live equity signals..."): 
        data_pool = fetch_master_dataset_pool(active_universe)

    if data_pool:
        current_market = {item["Name"]: item for item in data_pool}
        
        # --- STRATEGY SIGNAL FEED SCANNER ---
        st.subheader("📡 Live Strategy Signal Feed")
        signal_rows = []
        for name, asset in current_market.items():
            gann_up = "GANN UP" in asset["Gann Signal"]
            is_bullish = asset["is_bullish"]
            
            if name in st.session_state.stock_account["positions"]:
                status = "💼 Already in Portfolio"
            elif is_bullish and gann_up:
                status = "🟢 BUY SIGNAL GENERATED"
            else:
                status = "⚪ Scanning / Neutral"
                
            signal_rows.append({
                "Ticker": name,
                "Current Price": f"${asset['Price']:.2f}",
                "Gann Direction": asset["Gann Signal"],
                "Trend Structure": "🚀 BULLISH" if is_bullish else "⚠️ BEARISH",
                "System Action Alert": status
            })
        st.dataframe(pd.DataFrame(signal_rows), hide_index=True, use_container_width=True)

        # --- PORTFOLIO ORDER SUBMISSION INTERFACES ---
        st.markdown("---")
        st.subheader("🕹️ Equity Order Execution Pad")
        
        available_buys = [r["Ticker"] for r in signal_rows if "BUY SIGNAL" in r["System Action Alert"]]
        col_exec1, col_exec2 = st.columns(2)
        
        with col_exec1:
            if available_buys:
                selected_buy = st.selectbox("Select Active Signal Ticker to Buy", available_buys)
                if st.button(f"🚀 Execute Market BUY Order: {selected_buy}"):
                    if st.session_state.stock_account["cash"] >= trade_size:
                        price_now = current_market[selected_buy]["Price"]
                        st.session_state.stock_account["cash"] -= trade_size
                        st.session_state.stock_account["positions"][selected_buy] = {
                            "entry": price_now,
                            "size": trade_size,
                            "stop_loss": price_now * (1 - (max_risk / 100)),
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
                        }
                        save_stock_db(st.session_state.stock_account) # Save to Disk File
                        st.toast(f"Locked {selected_buy} into equity portfolio database!")
                        st.rerun()
                    else:
                        st.error("Insufficient Cash Pool.")
            else:
                st.info("No active structural buy alerts ready for deployment right now.")

        with col_exec2:
            active_owned = list(st.session_state.stock_account["positions"].keys())
            if active_owned:
                selected_exit = st.selectbox("Select Active Stock to Liquidate", active_owned)
                if st.button(f"🚨 Execute Market SELL Order: {selected_exit}"):
                    pos = st.session_state.stock_account["positions"][selected_exit]
                    price_now = current_market[selected_exit]["Price"]
                    
                    return_multiplier = price_now / pos["entry"]
                    liquidated_cash = pos["size"] * return_multiplier
                    pnl_pct = ((price_now - pos["entry"]) / pos["entry"]) * 100
                    pnl_cash = (pos["size"] / pos["entry"]) * (price_now - pos["entry"])
                    
                    st.session_state.stock_account["ledger"].append({
                        "Asset": selected_exit, "Entry Time": pos["timestamp"], "Exit Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Entry Price": f"${pos['entry']:.2f}", "Exit Price": f"${price_now:.2f}", "Reason": "🎯 MANUAL TARGET EXIT",
                        "Return %": f"{pnl_pct:+.2f}%", "Final P&L ($)": f"${pnl_cash:+.2f}"
                    })
                    st.session_state.stock_account["cash"] += liquidated_cash
                    del st.session_state.stock_account["positions"][selected_exit]
                    save_stock_db(st.session_state.stock_account) # Save to Disk File
                    st.toast(f"Successfully Sold {selected_exit}!")
                    st.rerun()
            else:
                st.info("No active stock positions to close manually.")

        # --- BACKGROUND PROTECTION AUTOMATION (Stop Loss Tracker) ---
        db_changed = False
        for name in list(st.session_state.stock_account["positions"].keys()):
            pos = st.session_state.stock_account["positions"][name]
            price = current_market[name]["Price"]
            
            if price <= pos["stop_loss"]:
                return_multiplier = price / pos["entry"]
                liquidated_cash = pos["size"] * return_multiplier
                pnl_pct = ((price - pos["entry"]) / pos["entry"]) * 100
                pnl_cash = (pos["size"] / pos["entry"]) * (price - pos["entry"])
                
                st.session_state.stock_account["ledger"].append({
                    "Asset": name, "Entry Time": pos["timestamp"], "Exit Time": datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Entry Price": f"${pos['entry']:.2f}", "Exit Price": f"${price:.2f}", "Reason": "🛑 STOP LOSS TRIGGERED",
                    "Return %": f"{pnl_pct:+.2f}%", "Final P&L ($)": f"${pnl_cash:+.2f}"
                })
                st.session_state.stock_account["cash"] += liquidated_cash
                del st.session_state.stock_account["positions"][name]
                db_changed = True
                st.toast(f"CRITICAL RISK ACTION: {name} hit hard Stop Loss limit.")
        
        if db_changed:
            save_stock_db(st.session_state.stock_account) # Save to Disk File
            st.rerun()

        # 4. LIVE ACCOUNT DASHBOARD METRICS DISPLAY
        open_positions = st.session_state.stock_account["positions"]
        current_floating_value = 0.0
        active_rows = []
        
        for name, pos in open_positions.items():
            curr_price = current_market[name]["Price"]
            pnl_pct = ((curr_price - pos["entry"]) / pos["entry"]) * 100
            pnl_cash = (pos["size"] / pos["entry"]) * (curr_price - pos["entry"])
            current_floating_value += (pos["size"] + pnl_cash)
            
            active_rows.append({
                "Asset": name, "Execution Time": pos["timestamp"], "Entry Price": f"${pos['entry']:.2f}",
                "Current Price": f"${curr_price:.2f}", "Stop Level": f"${pos['stop_loss']:.2f}",
                "Return Status": f"{pnl_pct:+.2f}%", "Floating P&L ($)": f"${pnl_cash:+.2f}"
            })

        total_equity = st.session_state.stock_account["cash"] + current_floating_value
        total_pnl = total_equity - 50000.00

        st.markdown("---")
        st.subheader("📋 Core Live Open Portfolio Account Status")
        m1, m2, m3 = st.columns(3)
        m1.metric("Available Balance Cash", f"${st.session_state.stock_account['cash']:,.2f} AUD")
        m2.metric("Total Net Portfolio Equity", f"${total_equity:,.2f} AUD")
        m3.metric("Net Total Realized Returns", f"${total_pnl:,.2f} AUD", delta=f"{total_pnl:+.2f}")

        if active_rows:
            st.dataframe(pd.DataFrame(active_rows), hide_index=True, use_container_width=True)
        else:
            st.info("Your portfolio is currently empty. Use the order pad above to execute active signals.")

        # 5. HISTORICAL RECORDS LEDGER
        st.markdown("---")
        st.subheader("📚 Historical Closed Ledger (Real-Time Performance Track)")
        if st.session_state.stock_account["ledger"]:
            ledger_df = pd.DataFrame(st.session_state.stock_account["ledger"])
            st.dataframe(ledger_df.iloc[::-1], hide_index=True, use_container_width=True)
        else:
            st.info("No closed trades archived yet for this session.")

elif app_mode == "Trend Momentum Screener":
    st.header(f"🟢 Elite Momentum Screener ({index_tier})")
    with st.spinner("Processing Index Matrix..."): data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        filtered = pd.DataFrame(data_pool)[pd.DataFrame(data_pool)["is_bullish"]==True].sort_values(by="Dist 52W High %")
        st.data_editor(filtered[['Name', 'Chart Link', 'Price', 'Gann Signal', 'Current Candle Type']], column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="$%.2f")}, disabled=True, hide_index=True, use_container_width=True)

elif app_mode == "Fundamental Value Searcher":
    st.header(f"💎 Fundamental Balance Sheet Matrix ({index_tier})")
    with st.spinner("Extracting Parameters..."): data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        st.data_editor(pd.DataFrame(data_pool)[['Name', 'Chart Link', 'Price', 'Trailing P/E', 'Profit Margin %', 'Div Yield %']], column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="$%.2f"), "Profit Margin %": st.column_config.NumberColumn(format="%.2f%%"), "Div Yield %": st.column_config.NumberColumn(format="%.2f%%")}, disabled=True, hide_index=True, use_container_width=True)

elif app_mode == "WD Gann Mechanical Screener":
    st.header(f"🦅 Advanced WD Gann Structural Matrix ({index_tier})")
    with st.spinner("Calculating Pivots..."): data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        st.data_editor(pd.DataFrame(data_pool)[['Name', 'Chart Link', 'Gann Signal', 'Current Candle Type', 'Price']], column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="$%.2f")}, disabled=True, hide_index=True, use_container_width=True)

elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Core Deep Research Terminal: {clean_symbol}")
    with st.spinner("Pulling real-time parameters..."): single_p = fetch_master_dataset_pool([target_ticker])
    if single_p:
        sd = single_p[0]
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Latest Close", f"${sd['Price']:.2f}")
        c2.metric("Gann Swing Direction", sd['Gann Signal'])
        c3.metric("Candle Structural State", sd['Current Candle Type'])
        c4.metric("Trend State (50/200MA)", "🚀 BULL" if sd['is_bullish'] else "⚠️ BEAR")

    components.html(f"""<div style="height:550px; width:100%;"><div id="tv_chart" style="height:100%; width:100%;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
      <script type="text/javascript">new TradingView.widget({{"autosize": true, "symbol": "ASX:{clean_symbol}", "interval": "D", "timezone": "Australia/Sydney", "theme": "light", "style": "1", "locale": "en", "container_id": "tv_chart"}});</script>
    </div>""", height=570)
