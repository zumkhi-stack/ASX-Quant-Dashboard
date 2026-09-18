@st.cache_data(ttl=1800)
def fetch_fundamental_insider_data(ticker_list):
    records = []
    if not ticker_list:
        return records

    for tk in ticker_list:
        try:
            display_name = tk.replace(".AX", "")
            t = Ticker(tk)
            
            # --- 1. Fetch Summary & Financial Data ---
            fin_data = t.financial_data.get(tk, {}) if isinstance(t.financial_data, dict) else {}
            curr_price = fin_data.get('currentPrice', np.nan)
            
            # Profit / Earnings Growth metric
            earnings_growth = fin_data.get('earningsGrowth', np.nan)
            
            calc_growth = np.nan
            if earnings_growth is not None and not np.isnan(earnings_growth):
                calc_growth = earnings_growth * 100

            # --- 2. Director / Insider Activity ---
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
                growth_badge = f"🟢 {calc_growth:+.2f}% (HIGH)"
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

        except Exception as e:
            continue

    return records
