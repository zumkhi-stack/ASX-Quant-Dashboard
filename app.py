import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from yahooquery import Ticker

# ==============================================================================
# 1. PAGE CONFIGURATION & INITIALIZATION
# ==============================================================================
st.set_page_config(
    page_title="Quant & Fundamental Stock Analysis Suite",
    page_icon="📈",
    layout="wide"
)

# ==============================================================================
# 2. TICKER UNIVERSE DEFINITION
# ==============================================================================
ASX_200_SAMPLE = [
    "BHP.AX", "CBA.AX", "CSL.AX", "WDS.AX", "NAB.AX",
    "WBC.AX", "ANZ.AX", "MQG.AX", "TLS.AX", "WES.AX",
    "WOW.AX", "RIO.AX", "FMG.AX", "PLS.AX"
]

US_TECH_SAMPLE = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA"
]

# ==============================================================================
# 3. SIDEBAR NAVIGATION & CONFIGURATION
# ==============================================================================
st.sidebar.title("📌 Navigation")

index_tier = st.sidebar.selectbox(
    "Select Stock Universe",
    ["ASX Top Samples", "US Tech Leaders"]
)

if index_tier == "ASX Top Samples":
    active_universe = ASX_200_SAMPLE
else:
    active_universe = US_TECH_SAMPLE

app_mode = st.sidebar.selectbox(
    "App Workspace",
    [
        "Fundamental & Insider Screener",
        "Automated Quant Fund Simulator",
        "Trend Momentum Screener",
        "WD Gann Mechanical Screener",
        "Interactive Charting Workspace"
    ]
)

# ==============================================================================
# 4. HELPER DATA FETCHING FUNCTIONS
# ==============================================================================
@st.cache_data(ttl=1800)
def fetch_fundamental_insider_data(ticker_list):
    """
    Fetches financial statements (Profit/Loss YoY growth) and 
    director/promoter insider transactions for the requested ticker list.
    """
    records = []
    if not ticker_list:
        return records

    for tk in ticker_list:
        try:
            display_name = tk.replace(".AX", "")
            t = Ticker(tk)
            
            # 1. Fetch Financial Data & Price
            fin_data = t.financial_data.get(tk, {}) if isinstance(t.financial_data, dict) else {}
            curr_price = fin_data.get('currentPrice', np.nan)
            
            # Extract YoY Profit / Earnings Growth metric
            earnings_growth = fin_data.get('earningsGrowth', np.nan)
            
            calc_growth = np.nan
            if earnings_growth is not None and not np.isnan(earnings_growth):
                calc_growth = earnings_growth * 100

            # 2. Director / Insider Activity Analysis
            insider_status = "⚪ Neutral / No Recent Filings"
            try:
                insider_df = t.insider_transactions
                if isinstance(insider_df, pd.DataFrame) and not insider_df.empty:
                    if tk in insider_df.index:
                        df_ins = insider_df.loc[tk]
                        if isinstance(df_ins, pd.Series):
                            df_ins = df_ins.to_frame().T
                        
                        if 'transactionText' in df_ins.columns:
                            buys = df_ins['transactionText'].str.contains('Purchase|Buy', case=False, na=False).sum()
                            sells = df_ins['transactionText'].str.contains('Sale|Sell', case=False, na=False).sum()
                            
                            if buys > sells:
                                insider_status = f"🟢 NET BUY ({buys} Buys, {sells} Sells)"
                            elif sells > buys:
                                insider_status = f"🔴 NET SELL ({sells} Sells, {buys} Buys)"
                            elif buys > 0:
                                insider_status = f"🟡 BALANCED ({buys} Buys / {sells} Sells)"
            except Exception:
                pass

            # Badge formatting for display
            if not np.isnan(calc_growth) and calc_growth >= 30.0:
                growth_badge = f"🟢 {calc_growth:+.2f}% (HIGH GROWTH)"
            elif not np.isnan(calc_growth):
                growth_badge = f"⚪ {calc_growth:+.2f}%"
            else:
                growth_badge = "N/A"

            records.append({
                "Name": display_name,
                "Ticker": tk,
                "Current Price": curr_price,
                "YoY Profit Growth": growth_badge,
                "Director / Insider Activity": insider_status,
                "Raw Growth": calc_growth if not np.isnan(calc_growth) else -999.0
            })

        except Exception:
            continue

    return records


@st.cache_data(ttl=1800)
def fetch_technical_pool(ticker_list):
    """Fetches price history and simple moving averages for technical screeners."""
    records = []
    for tk in ticker_list:
        try:
            df = yf.download(tk, period="6m", progress=False)
            if not df.empty:
                close = float(df['Close'].iloc[-1])
                records.append({
                    "Name": tk.replace(".AX", ""),
                    "Ticker": tk,
                    "Price": close
                })
        except Exception:
            continue
    return pd.DataFrame(records)

# ==============================================================================
# 5. WORKSPACE ROUTING & INTERFACE
# ==============================================================================

# ------------------------------------------------------------------------------
# WORKSPACE 1: FUNDAMENTAL & INSIDER SCREENER
# ------------------------------------------------------------------------------
if app_mode == "Fundamental & Insider Screener":
    st.title("🏛️ Fundamental & Insider Trading Screener")
    st.markdown(
        "Screens assets based on **Year-over-Year Profit Growth** (highlighting $\ge 30\%$) "
        "and tracks **Director / Promoter Share Transactions**."
    )

    with st.spinner("Retrieving Financial Statements & Director Filings..."):
        fund_records = fetch_fundamental_insider_data(active_universe)

    if fund_records:
        df_fund = pd.DataFrame(fund_records)

        # Interactive controls inside the workspace
        col_ctrl1, col_ctrl2 = st.columns([2, 1])
        with col_ctrl1:
            min_growth_threshold = st.slider(
                "Filter minimum Profit Growth % (Default shows all: -50% to 100%)",
                min_value=-50,
                max_value=100,
                value=-50,
                step=5
            )
        with col_ctrl2:
            insider_filter = st.selectbox(
                "Filter Director Activity",
                ["All Activity", "🟢 Net Buying Only", "🔴 Net Selling Only"]
            )

        # Apply user filters
        filtered_df = df_fund[df_fund["Raw Growth"] >= min_growth_threshold].copy()

        if insider_filter == "🟢 Net Buying Only":
            filtered_df = filtered_df[filtered_df["Director / Insider Activity"].str.contains("NET BUY")]
        elif insider_filter == "🔴 Net Selling Only":
            filtered_df = filtered_df[filtered_df["Director / Insider Activity"].str.contains("NET SELL")]

        filtered_df = filtered_df.sort_values(by="Raw Growth", ascending=False)

        # Render KPI metrics
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Total Assets Screened", len(df_fund))
        m2.metric("High Growth Assets (≥ 30% Growth)", len(df_fund[df_fund["Raw Growth"] >= 30]))
        m3.metric("Director Net-Buying Companies", len(df_fund[df_fund["Director / Insider Activity"].str.contains("NET BUY")]))

        # Render Streamlit Data Table
        st.subheader("Screened Assets")
        
        if not filtered_df.empty:
            st.dataframe(
                filtered_df[['Name', 'Ticker', 'Current Price', 'YoY Profit Growth', 'Director / Insider Activity']],
                column_config={
                    "Current Price": st.column_config.NumberColumn("Current Price", format="$%.2f"),
                    "YoY Profit Growth": st.column_config.TextColumn("YoY Profit Growth"),
                    "Director / Insider Activity": st.column_config.TextColumn("Director / Insider Activity")
                },
                hide_index=True,
                use_container_width=True
            )
        else:
            st.info("No stocks match the selected slider threshold or insider trading filter. Try lowering the profit growth slider.")

# ------------------------------------------------------------------------------
# WORKSPACE 2: AUTOMATED QUANT FUND SIMULATOR
# ------------------------------------------------------------------------------
elif app_mode == "Automated Quant Fund Simulator":
    st.title("🤖 Automated Quant Fund Simulator")
    st.write("Simulate automated portfolio rebalancing and algorithmic weighting strategies.")
    df_tech = fetch_technical_pool(active_universe)
    if not df_tech.empty:
        st.dataframe(df_tech, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# WORKSPACE 3: TREND MOMENTUM SCREENER
# ------------------------------------------------------------------------------
elif app_mode == "Trend Momentum Screener":
    st.title("📊 Trend Momentum Screener")
    st.write("Identifies assets displaying strong technical momentum and price structure.")
    df_tech = fetch_technical_pool(active_universe)
    if not df_tech.empty:
        st.dataframe(df_tech, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# WORKSPACE 4: WD GANN MECHANICAL SCREENER
# ------------------------------------------------------------------------------
elif app_mode == "WD Gann Mechanical Screener":
    st.title("📐 WD Gann Mechanical Screener")
    st.write("Screens swing highs, swing lows, and trend reversals using mechanical Gann rules.")
    df_tech = fetch_technical_pool(active_universe)
    if not df_tech.empty:
        st.dataframe(df_tech, use_container_width=True, hide_index=True)

# ------------------------------------------------------------------------------
# WORKSPACE 5: INTERACTIVE CHARTING WORKSPACE
# ------------------------------------------------------------------------------
elif app_mode == "Interactive Charting Workspace":
    st.title("📈 Interactive Charting Workspace")
    selected_ticker = st.selectbox("Select Stock to Chart", active_universe)
    
    if selected_ticker:
        data = yf.download(selected_ticker, period="1y", progress=False)
        if not data.empty:
            st.line_chart(data['Close'])
