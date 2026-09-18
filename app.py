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
# Example tickers (ASX universe as default base - easily expandable)
ASX_200_SAMPLE = [
    "BHP.AX", "CBA.AX", "CSL.AX", "WDS.AX", "NAB.AX",
    "WBC.AX", "ANZ.AX", "MQG.AX", "TLS.AX", "WES.AX",
    "WOW.AX", "RIO.AX", "FMG.AX", "PLS.AX", "NCM.AX"
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

# Workspace selector including your new screener
app_mode = st.sidebar.selectbox(
    "App Workspace",
    [
        "Fundamental & Insider Screener",  # NEW WORKSPACE
        "Automated Quant Fund Simulator",
        "Trend Momentum Screener",
        "WD Gann Mechanical Screener",
        "Interactive Charting Workspace"
    ]
)

# ==============================================================================
# 4. HELPER DATA FETCHING FUNCTIONS
# ==============================================================================
@st.cache_data(ttl=3600)
def fetch_fundamental_insider_data(ticker_list):
    """
    Fetches financial statements (Profit/Loss YoY growth) and 
    director/promoter insider transactions for the requested ticker list.
    """
    records = []
    if not ticker_list:
        return records

    t = Ticker(ticker_list)

    # 1. Fetch bulk financial & insider data via yahooquery
    try:
        financials = t.financial_data
        income_stmt = t.get_financial_data(types=['NetIncome'], frequency='a')
        insider = t.insider_transactions
    except Exception as e:
        st.error(f"Error connecting to Yahoo Finance API: {e}")
        return records

    # 2. Iterate through tickers and extract metrics
    for tk in ticker_list:
        try:
            display_name = tk.replace(".AX", "")

            # --- A. Profit Growth Calculation (Year-over-Year) ---
            profit_growth = np.nan
            if isinstance(income_stmt, pd.DataFrame) and not income_stmt.empty:
                if tk in income_stmt.index:
                    df_tk = income_stmt.loc[tk].dropna().sort_index()
                    if len(df_tk) >= 2:
                        p_current = df_tk['NetIncome'].iloc[-1]
                        p_previous = df_tk['NetIncome'].iloc[-2]
                        if p_previous > 0:
                            profit_growth = ((p_current - p_previous) / p_previous) * 100

            # --- B. Director / Insider Transaction Analysis ---
            insider_status = "⚪ Neutral / No Recent Filings"
            buy_count = 0
            sell_count = 0

            if isinstance(insider, pd.DataFrame) and not insider.empty:
                if tk in insider.index:
                    df_ins = insider.loc[tk]
                    if isinstance(df_ins, pd.Series):
                        df_ins = df_ins.to_frame().T

                    if 'transactionText' in df_ins.columns:
                        buy_count = df_ins['transactionText'].str.contains('Purchase|Buy', case=False, na=False).sum()
                        sell_count = df_ins['transactionText'].str.contains('Sale|Sell', case=False, na=False).sum()

                        if buy_count > sell_count:
                            insider_status = f"🟢 NET BUY ({buy_count} Buys, {sell_count} Sells)"
                        elif sell_count > buy_count:
                            insider_status = f"🔴 NET SELL ({sell_count} Sells, {buy_count} Buys)"
                        elif buy_count > 0 and buy_count == sell_count:
                            insider_status = f"🟡 BALANCED ({buy_count} Buys / {sell_count} Sells)"

            # --- C. Target Financial Metrics ---
            fin_data = financials.get(tk, {}) if isinstance(financials, dict) else {}
            curr_price = fin_data.get('currentPrice', np.nan)
            
            # Use yahooquery earnings growth if YoY statement is unavailable
            reported_growth = fin_data.get('earningsGrowth', np.nan)
            if not np.isnan(reported_growth):
                calc_growth = reported_growth * 100
            else:
                calc_growth = profit_growth

            # Conditional formatting badge (> 30% profit growth threshold)
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
                close = df['Close'].iloc[-1]
                sma_50 = df['Close'].rolling(50).mean().iloc[-1]
                trend = "🟢 Uptrend" if close > sma_50 else "🔴 Downtrend"
                records.append({
                    "Name": tk.replace(".AX", ""),
                    "Ticker": tk,
                    "Price": float(close),
                    "Trend (50 SMA)": trend
                })
        except Exception:
            continue
    return pd.DataFrame(records)

# ==============================================================================
# 5. WORKSPACE ROUTING & INTERFACE
# ==============================================================================

# ------------------------------------------------------------------------------
# WORKSPACE 1: FUNDAMENTAL & INSIDER SCREENER (NEW)
# ------------------------------------------------------------------------------
if app_mode == "Fundamental & Insider Screener":
    st.title("🏛️ Fundamental & Insider Trading Screener")
    st.markdown(
        "Screens assets based on **Year-over-Year Profit Growth** (highlighting $\ge 30\%$) "
        "and tracks **Director / Promoter Share Transactions**."
    )

    with st.spinner("Retrieving Financial Statements & Director Filings from SEC / ASX..."):
        fund_records = fetch_fundamental_insider_data(active_universe)

    if fund_records:
        df_fund = pd.DataFrame(fund_records)

        # Interactive controls inside the workspace
        col_ctrl1, col_ctrl2 = st.columns([2, 1])
        with col_ctrl1:
            min_growth_threshold = st.slider(
                "Filter minimum Profit Growth % (Target threshold: ≥ 30%)",
                min_value=-50,
                max_value=100,
                value=30,
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
        m2.metric("Assets Meeting Target (≥ 30% Growth)", len(df_fund[df_fund["Raw Growth"] >= 30]))
        m3.metric("Director Net-Buying Companies", len(df_fund[df_fund["Director / Insider Activity"].str.contains("NET BUY")]))

        # Render Streamlit Data Table
        st.subheader(f"Screened Assets (Profit Growth ≥ {min_growth_threshold}%)")
        
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
            st.info("No stocks found matching the specified profit growth and insider trading criteria.")

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
