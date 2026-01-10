import yfinance as yf


tickers = [

    # Top 50 (Originals & Heavyweights)
    "AAPL", "MSFT", "NVDA", "AMZN", "META", "GOOGL", "GOOG", "AVGO", "TSLA", "BRK-B",
    "LLY", "UNH", "JPM", "V", "XOM", "MA", "COST", "PG", "HD", "JNJ",
    "ORCL", "BAC", "ABBV", "CVX", "WMT", "KO", "CRM", "MRK", "PEP", "ADBE",
    "LIN", "ACN", "TMO", "MCD", "CSCO", "ABT", "TMUS", "QCOM", "TXN", "DHR",
    "INTC", "VZ", "AMD", "WFC", "IBM", "CAT", "AXP", "MS", "GE", "PM",

    # 51 - 100
    "AMAT", "ISRG", "LOW", "PFE", "INTU", "NEE", "GS", "UBER", "HON", "PLTR",
    "BKNG", "SPGI", "UNP", "SYK", "SYY", "ETN", "LMT", "BLK", "NOW", "COP",
    "ADI", "SCHW", "TJX", "VRTX", "GEV", "REGN", "MDLZ", "MDT", "C", "MMC",
    "ABNB", "ZTS", "BSX", "AMT", "CB", "PANW", "FI", "PLD", "CI", "LRCX",
    "ELV", "ADP", "BA", "SBUX", "DE", "ICE", "GILD", "MO", "PGR", "HCA",

    # 101 - 150
    "MU", "APH", "KLAC", "CME", "ORLY", "SNPS", "EOG", "CDNS", "MCK", "WM",
    "ITW", "USB", "T", "SHW", "MAR", "BDX", "PH", "CL", "SLB", "EMR",
    "EW", "GD", "AON", "CVS", "ROP", "NXPI", "MCO", "ECL", "MSI", "PSX",
    "FDX", "TT", "ADSK", "TDG", "DASH", "MPC", "WELL", "MCHP", "NSC", "TFC",
    "NKE", "PCAR", "D", "KMB", "F", "MNST", "AZO", "GM", "AJG", "O",

    # 151 - 200
    "MET", "CMG", "TRV", "CTAS", "CHTR", "CRWD", "RMD", "CARR", "DXCM", "AIG",
    "PSA", "KR", "WMB", "OKE", "KDP", "OXY", "HWM", "TEL", "JCI", "SPG",
    "PAYX", "PCG", "RSG", "VLO", "NOC", "GEHC", "GWW", "FTNT", "AHH", "BK",
    "AMP", "DOW", "URI", "CSX", "KHC", "HLT", "BKR", "A", "IQV", "DLR",
    "ALL", "AME", "CMI", "AMC", "STZ", "AEP", "PRU", "PRX", "VRSK", "KVUE",

    # 201 - 250
    "OTIS", "COR", "EIX", "ED", "FAST", "STT", "SBAC", "KEYS", "WBD", "WDC",
    "PEG", "ROST", "DLTR", "XYL", "SYF", "EXC", "K", "DHI", "CNC", "MTD",
    "NEM", "HPQ", "CTSH", "GLW", "TRGP", "IDXX", "WST", "ANET", "EA", "EFX",
    "LYB", "CBRE", "AWK", "ODFL", "BBY", "MTB", "GPN", "EBAY", "ETSY", "FITB",
    "RJF", "HUBB", "WEC", "VMC", "STX", "FE", "LEN", "DVN", "ZBH", "BRO"
]

if __name__ == "__main__":
    start = "2013-01-01"
    end = "2024-12-31"
    start_year = start[0:4]
    end_year = end[0:4]

    complete_data = yf.download(tickers, start=start, end=end)  # Meta IPO 2012

    # Check what columns exist
    print(complete_data.columns.levels[0])

    # Use "Close" instead of "Adj Close"
    if "Adj Close" in complete_data.columns.levels[0]:
        target_price_data = complete_data["Adj Close"]
    else:
        target_price_data = complete_data["Close"]

    target_price_data.to_csv(f"data/{len(tickers)}stocks_close_{start_year}_{end_year}.csv")

    print("Saved closing prices:", target_price_data.shape)


