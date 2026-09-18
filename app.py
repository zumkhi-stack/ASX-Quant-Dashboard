import streamlit as st
import pandas as pd
import numpy as np
from yahooquery import Ticker
import streamlit.components.v1 as components
from datetime import datetime

# ==============================================================================
# 1. PAGE CONFIGURATION & INITIALIZATION
# ==============================================================================
st.set_page_config(page_title="ASX Master Quantitative Command Center", layout="wide")
st.title("📊 ASX Master Quantitative Command Center")

# --- TICKER TAPE UNIVERSE INDEX ---
components.html("""
<div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
<script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
{"symbols": [{"proName": "INDEX:XJO", "title": "ASX 200 Index"}, {"proName": "ASX:BHP", "title": "BHP Group"}, {"proName": "ASX:CBA", "title": "Commonwealth Bank"}, {"proName": "ASX:WBC", "title": "Westpac"}], "colorTheme": "light", "displayMode": "adaptive", "locale": "en"}
</script></div>""", height=50)

# ==============================================================================
# 2. FULL UNIVERSE ARRAYS DEFINITION
# ==============================================================================
ASX_50 = [
    "BHP.AX", "CBA.AX", "WBC.AX", "NAB.AX", "ANZ.AX", "MQG.AX", "WES.AX", "RIO.AX", "FMG.AX", "CSL.AX",
    "WDS.AX", "TLS.AX", "TCL.AX", "WOW.AX", "QBE.AX", "GMG.AX", "MIN.AX", "APA.AX", "QAN.AX", "SPK.AX",
    "REA.AX", "ALL.AX", "SHL.AX", "COH.AX", "IPL.AX", "BSL.AX", "PPT.AX", "WHC.AX", "ALQ.AX", "LYC.AX",
    "BEN.AX", "BOQ.AX", "BLD.AX", "CAR.AX", "SGP.AX", "DXS.AX", "CHC.AX", "GPT.AX", "MGR.AX", "VCX.AX",
    "AZJ.AX", "A2M.AX", "AMP.AX", "ANN.AX", "AST.AX", "ALX.AX", "EVN.AX", "IAG.AX", "MPL.AX", "SUN.AX"
]

ASX_100_ADDITIONS = [
    "ALU.AX", "APE.AX", "ARS.AX", "AWC.AX", "BKW.AX", "BWP.AX", "BXB.AX", "CGF.AX", "CIN.AX", "CLW.AX",
    "CNI.AX", "COL.AX", "CPU.AX", "CQR.AX", "CSR.AX", "CTC.AX", "CWN.AX", "CYP.AX", "EHE.AX", "ELD.AX",
    "FLT.AX", "FPH.AX", "GEM.AX", "GOZ.AX", "HDN.AX", "HLI.AX", "HVN.AX", "IEL.AX", "IFL.AX", "IFT.AX",
    "ILU.AX", "JBH.AX", "JHX.AX", "LLC.AX", "LNK.AX", "MND.AX"
]

ASX_200_ADDITIONS = [
    "A2B.AX", "ABG.AX", "AFI.AX", "AGL.AX", "AIN.AX", "ALK.AX", "AMI.AX", "ANG.AX", "AO1.AX", "API.AX",
    "APM.AX", "APX.AX", "ARB.AX", "ARE.AX", "ARG.AX", "ARU.AX", "ASB.AX", "ASM.AX", "ASG.AX", "ASX.AX",
    "AUB.AX", "AVN.AX", "AVV.AX", "AWE.AX", "AWI.AX", "AX1.AX", "AZS.AX", "B4P.AX", "BAB.AX", "BAL.AX",
    "BAP.AX", "BCB.AX", "BCI.AX", "BFL.AX", "BGA.AX", "BGL.AX", "BGP.AX", "BIF.AX", "BKI.AX", "BKL.AX",
    "BLX.AX", "BML.AX", "BMT.AX", "BNA.AX", "BNL.AX", "BOA.AX", "BOT.AX", "BOU.AX", "BPT.AX", "BRG.AX",
    "BRL.AX", "BRU.AX", "BTI.AX", "BTR.AX", "BVS.AX", "C6C.AX", "CAE.AX", "CAF.AX", "CAJ.AX", "CCV.AX",
    "CDA.AX", "CDD.AX", "CDP.AX", "CE1.AX", "CEL.AX", "CEN.AX", "CGC.AX", "CHH.AX", "CHL.AX", "CHR.AX",
    "CIE.AX", "CIM.AX", "CIP.AX", "CKF.AX", "CLA.AX", "CLH.AX", "CLQ.AX", "CLV.AX", "CMW.AX", "CNU.AX", "COB.AX"
]

# ==============================================================================
# 3. SIDEBAR NAVIGATION & FILTERS
# ==============================================================================
st.sidebar.header("🛡️ Strategy Universe Selector")
index_tier = st.sidebar.selectbox("Choose Core Index Target", ["ASX 50", "ASX 100", "ASX 200"])

if index_tier == "ASX 50":
    active_universe = ASX_50
elif index_tier == "ASX 100":
    active_universe = sorted(list(set(ASX_50 + ASX_100_ADDITIONS)))
else:
    active_universe = sorted(list(set(ASX_50 + ASX_100_ADDITIONS + ASX_200_ADDITIONS)))

raw_search = st.sidebar.text_input("Stock Search (e.g. PLS, REA, BHP)", "").strip().upper()
app_mode = st.sidebar.selectbox(
    "App Workspace", 
    [
        "Fundamental & Insider Screener",
        "Automated Quant Fund Simulator", 
        "Trend Momentum Screener", 
        "Fundamental Value Searcher", 
        "WD Gann Mechanical Screener", 
        "Interactive Charting Workspace"
    ]
)

if raw_search:
    target_ticker = raw_search if raw_search.endswith(".AX") else f"{raw_search}.AX"
    clean_symbol = raw_search.split('.')[0]
else:
    target_ticker = st.sidebar.selectbox("Select Active Asset", active_universe) if app_mode == "Interactive Charting Workspace" else active_universe[0]
    clean_symbol = target_ticker.replace(".AX", "")

# ==============================================================================
# 4. MASTER DATA FETCHING POOLS
# ==============================================================================
@st.cache_data(ttl=300)
def fetch_master_dataset_pool(ticker_list):
    compiled_results = []
    if not ticker_list: 
        return []
    try:
        t = Ticker(ticker_list)
        history = t.history(period="1y")
        if history is None or (isinstance(history, pd.DataFrame) and history.empty): 
            return []
        
        summary = getattr(t, 'summary_detail', {})
        financials = getattr(t, 'financial_data', {})
    except Exception: 
        return []

    cm, cd = datetime.now().month, datetime.now().day
    is_node, n_type = False, ""
    for m, d, t_name in [(3,21,"CARDINAL"),(6,22,"CARDINAL"),(9,23,"CARDINAL"),(12,22,"CARDINAL"),(2,4,"FIXED"),(5,6,"FIXED"),(8,9,"FIXED"),(11,7,"FIXED")]:
        if cm == m and abs(cd - d) <= 2: 
            is_node, n_type = True, f" [{t_name}]"

    for tk in ticker_list:
        try:
            if isinstance(history.index, pd.MultiIndex):
                if tk not in history.index.levels[0]: 
                    continue
                df = history.loc[tk].dropna().copy()
            else: 
                df = history.dropna().copy()
                
            if df.empty or len(df) < 5: 
                continue

            c_col = 'adjclose' if 'adjclose' in df.columns else 'close'
            df['50_MA'] = df[c_col].rolling(window=min(50, len(df))).mean()
            df['200_MA'] = df[c_col].rolling(window=min(200, len(df))).mean()
            
            p_curr = float(df[c_col].iloc[-1])
            p_prev = float(df[c_col].iloc[-2]) if len(df) > 1 else p_curr
            h_52w = float(df['high'].max())
            d_high = ((h_52w - p_curr) / h_52w) * 100 if h_52w > 0 else 0
            is_bull = float(df['50_MA'].iloc[-1]) > float(df['200_MA'].iloc[-1]) if len(df) >= 50 else True

            df['ph'] = df['high'].shift(1)
            df['pl'] = df['low'].shift(1)
            lr = df.iloc[-1]
            h, l, ph, pl = lr['high'], lr['low'], lr['ph'], lr['pl']
            
            b_type = "🟠 Outside Bar" if (h > ph and l < pl) else ("⚪ Inside Bar" if (h <= ph and l >= pl) else ("🟢 Up Bar" if h > ph else "🔴 Down Bar"))

            s_dir = 1
            highs = df['high'].values
            lows = df['low'].values
            for i in range(2, len(df)):
                if highs[i] > highs[i-2] and s_dir == -1: 
                    s_dir = 1
                elif lows[i] < lows[i-2] and s_dir == 1: 
                    s_dir = -1
                    
            g_sig = "🟢 GANN UP" if s_dir == 1 else "🚨 GANN DOWN"
            if is_node: 
                g_sig += f" ⚡{n_type}"

            t_sum = summary.get(tk, {}) if isinstance(summary, dict) else {}
            t_fin = financials.get(tk, {}) if isinstance(financials, dict) else {}
            r_name = tk.replace(".AX", "")
            l_url = f"https://www.tradingview.com/chart/?symbol=ASX:{r_name}"

            pe_val = t_sum.get('trailingPE', np.nan) if isinstance(t_sum, dict) else np.nan
            pm_raw = t_fin.get('profitMargins') if isinstance(t_fin, dict) else None
            pm_val = pm_raw * 100 if pm_raw is not None and isinstance(pm_raw, (int, float)) else np.nan
            
            dy_raw = t_sum.get('dividendYield') if isinstance(t_sum, dict) else None
            dy_val = dy_raw * 100 if dy_raw is not None and isinstance(dy_raw, (int, float)) else np.nan

            compiled_results.append({
                "Ticker": tk, 
                "Chart Link": l_url, 
                "Name": r_name, 
                "Entry Price": p_prev, 
                "Price": p_curr, 
                "Dist 52W High %": d_high, 
                "is_bullish": is_bull, 
                "Gann Signal": g_sig, 
                "Current Candle Type": b_type, 
                "Trailing P/E": pe_val, 
                "Profit Margin %": pm_val, 
                "Div Yield %": dy_val
            })
        except Exception: 
            continue
            
    return compiled_results

# ==============================================================================
# 5. WORKSPACES INTERFACE ROUTING
# ==============================================================================

# --- WORKSPACE 1: FUNDAMENTAL & INSIDER SCREENER ---
if app_mode == "Fundamental & Insider Screener":
    st.header(f"🏛️ Fundamental Stock Screener ({index_tier})")
    st.caption("Screens assets by live Profit Margins and Dividend Yield metrics.")

    with st.spinner("Fetching Market Data..."):
        data_pool = fetch_master_dataset_pool(active_universe)

    if data_pool:
        df_fund = pd.DataFrame(data_pool)
        
        # User Controls
        c1, c2 = st.columns(2)
        with c1:
            min_margin = st.slider("Filter Minimum Profit Margin %", -50.0, 50.0, -50.0, 1.0)
        with c2:
            min_div = st.slider("Filter Minimum Dividend Yield %", 0.0, 15.0, 0.0, 0.5)

        # Filter out NaN rows cleanly for sliders
        df_display = df_fund.copy()
        
        # Apply Sliders
        filtered_df = df_display[
            (df_display["Profit Margin %"].fillna(-999) >= min_margin) & 
            (df_display["Div Yield %"].fillna(0) >= min_div)
        ]

        st.divider()
        m1, m2 = st.columns(2)
        m1.metric("Total Assets Fetched", len(df_fund))
        m2.metric("Filtered Results", len(filtered_df))

        # Render Table Directly
        st.dataframe(
            filtered_df[['Name', 'Ticker', 'Price', 'Profit Margin %', 'Div Yield %', 'Trailing P/E', 'Chart Link']],
            use_container_width=True,
            hide_index=True
        )

# --- WORKSPACE 2: AUTOMATED QUANT FUND SIMULATOR ---
elif app_mode == "Automated Quant Fund Simulator":
    st.header("⚙️ ASX Blue Chip Manual Execution Terminal")

    if "stock_account" not in st.session_state:
        st.session_state.stock_account = {"cash": 50000.00, "positions": {}, "ledger": []}

    st.sidebar.subheader("⚙️ Automated Rule Configurations")
    max_risk = st.sidebar.slider("Max Trailing Stop-Loss %", 1.0, 15.0, 5.0, step=0.5)
    trade_size = st.sidebar.number_input("Fixed Size Per Trade ($ AUD Units)", value=10000, step=1000)

    if st.sidebar.button("Wipe Sandbox & Reset Cash"):
        st.session_state.stock_account = {"cash": 50000.00, "positions": {}, "ledger": []}
        st.rerun()

    with st.spinner("Processing live equity signals..."): 
        data_pool = fetch_master_dataset_pool(active_universe)

    if data_pool:
        current_market = {item["Name"]: item for item in data_pool}
        
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
                        st.toast(f"Locked {selected_buy} into equity portfolio!")
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
                    st.toast(f"Successfully Sold {selected_exit}!")
                    st.rerun()
            else:
                st.info("No active stock positions to close manually.")

        open_positions = st.session_state.stock_account["positions"]
        current_floating_value = 0.0
        active_rows = []
        
        for name, pos in open_positions.items():
            curr_price = current_market.get(name, {}).get("Price", pos["entry"])
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
            st.info("Your portfolio is currently empty.")

# --- WORKSPACE 3: TREND MOMENTUM SCREENER ---
elif app_mode == "Trend Momentum Screener":
    st.header(f"🟢 Elite Momentum Screener ({index_tier})")
    with st.spinner("Processing Index Matrix..."): 
        data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        df_pool = pd.DataFrame(data_pool)
        filtered = df_pool[df_pool["is_bullish"] == True].sort_values(by="Dist 52W High %")
        st.data_editor(
            filtered[['Name', 'Chart Link', 'Price', 'Gann Signal', 'Current Candle Type']], 
            column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="$%.2f")}, 
            disabled=True, hide_index=True, use_container_width=True
        )

# --- WORKSPACE 4: FUNDAMENTAL VALUE SEARCHER ---
elif app_mode == "Fundamental Value Searcher":
    st.header(f"💎 Fundamental Balance Sheet Matrix ({index_tier})")
    with st.spinner("Extracting Parameters..."): 
        data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        st.data_editor(
            pd.DataFrame(data_pool)[['Name', 'Chart Link', 'Price', 'Trailing P/E', 'Profit Margin %', 'Div Yield %']], 
            column_config={
                "Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), 
                "Price": st.column_config.NumberColumn(format="$%.2f"), 
                "Profit Margin %": st.column_config.NumberColumn(format="%.2f%%"), 
                "Div Yield %": st.column_config.NumberColumn(format="%.2f%%")
            }, 
            disabled=True, hide_index=True, use_container_width=True
        )

# --- WORKSPACE 5: WD GANN MECHANICAL SCREENER ---
elif app_mode == "WD Gann Mechanical Screener":
    st.header(f"🦅 Advanced WD Gann Structural Matrix ({index_tier})")
    with st.spinner("Calculating Pivots..."): 
        data_pool = fetch_master_dataset_pool(active_universe)
    if data_pool:
        st.data_editor(
            pd.DataFrame(data_pool)[['Name', 'Chart Link', 'Gann Signal', 'Current Candle Type', 'Price']], 
            column_config={"Chart Link": st.column_config.LinkColumn("Chart", display_text="📈 View"), "Price": st.column_config.NumberColumn(format="$%.2f")}, 
            disabled=True, hide_index=True, use_container_width=True
        )

# --- WORKSPACE 6: INTERACTIVE CHARTING WORKSPACE ---
elif app_mode == "Interactive Charting Workspace":
    st.header(f"📈 Core Deep Research Terminal: {clean_symbol}")
    with st.spinner("Pulling real-time parameters..."): 
        single_p = fetch_master_dataset_pool([target_ticker])
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
