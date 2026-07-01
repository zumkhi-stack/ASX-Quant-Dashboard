import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime
import json
import os

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

# --- BACKEND CORE ENGINE FUNCTION ---
def fetch_master_dataset_pool(tickers):
    """Fetches market metrics using Yahooquery and simulates core quantitative data shapes."""
    try:
        t = Ticker(tickers, asynchronous=True)
        prices = t.price
        data_list = []
        for ticker in tickers:
            p_data = prices.get(ticker, {})
            if isinstance(p_data, dict) and "regularMarketPrice" in p_data:
                curr_price = p_data["regularMarketPrice"]
                # Simulating structural signal generation engine parameters
                gann_state = "GANN UP 🟩" if np.random.rand() > 0.4 else "GANN DOWN 🚨"
                is_bull = True if "UP" in gann_state else False
                data_list.append({
                    "Name": ticker,
                    "Price": curr_price,
                    "Gann Signal": gann_state,
                    "is_bullish": is_bull
                })
        return data_list
    except Exception as e:
        st.error(f"Data engine error: {e}")
        return []

# --- NAVIGATION ROUTING INTERFACE ---
st.sidebar.header("🛡️ Strategy Control Hub")
index_tier = st.sidebar.selectbox("Choose Core Index Target", ["ASX 50", "ASX 100", "ASX 200"])
app_mode = st.sidebar.radio("Navigate Workspace Domain", ["Automated Quant Fund Simulator", "Trend Momentum Screener"])

# --- WORKSPACE ROUTING DOMAIN ---
if app_mode == "Automated Quant Fund Simulator":
    st.header("⚙️ ASX Blue Chip Manual Execution Terminal (Persistent Storage)")
    st.caption("Positions are saved permanently to disk and will survive page reloads and server restarts completely.")

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

    # Initialize / Load data from file storage directly into memory session frame
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

    # 3. Flat Universe Selection Dictionary Mapping (No Indentation Blocks)
    u_map = {
        "ASX 50": ASX_50, 
        "ASX 100": ASX_50 + ASX_100_ADDITIONS, 
        "ASX 200": ASX_50 + ASX_100_ADDITIONS + ASX_200_ADDITIONS
    }
    selected_universe = u_map.get(index_tier, ASX_50)

    with st.spinner("Processing live equity signals..."): 
        data_pool = fetch_master_dataset_pool(selected_universe)

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
                        save_stock_db(st.session_state.stock_account)
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
                    save_stock_db(st.session_state.stock_account)
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
            save_stock_db(st.session_state.stock_account)
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
    st.header("📡 Market Trend Momentum Technical Screener")
    st.info("Workspace logic goes here.")
