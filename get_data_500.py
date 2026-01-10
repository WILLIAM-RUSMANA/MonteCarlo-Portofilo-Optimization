import yfinance as yf


tickers = [
    "NVDA", "AAPL", "MSFT", "AMZN", "META", "AVGO", "GOOGL", "TSLA", "BRK-B", "LLY", "WMT", "JPM", "V", "ORCL", "MA", "XOM", "JNJ", "BAC", "PLTR", "COST", "ABBV",
    "NFLX", "MU", "HD", "AMD", "GE", "PG", "CVX", "UNH", "WFC", "MS", "CSCO", "CAT", "IBM", "GS", "INTU", "AXP", "PM", "ABT", "ISRG", "LOW", "NOW", "ACN", "RTX",
    "TXN", "PEP", "BKNG", "QCOM", "PGR", "SPGI", "BA", "TMO", "SCHW", "TJX", "NEE", "AMGN", "HON", "BLK", "C", "UNP", "GILD", "CMCSA", "AMAT", "ADP", "PFE", 
    "SYK", "DE", "ETN", "GEV", "PANW", "DHR", "COF", "TMUS", "MMC", "VRTX", "COP", "ADI", "MDT", "CB", "CRWD", "LRCX", "APH", "KLAC", "CME", "MO", "BX", "ICE",
    "AMT", "LMT", "SO", "PLD", "ANET", "BMY", "TT", "SBUX", "ELV", "FI", "DUK", "WELL", "MCK", "CEG", "INTC", "CDNS", "CI", "AJG", "WM", "PH", "MDLZ", "EQIX",
    "SHW", "MMM", "KKR", "TDG", "ORLY", "CVS", "SNPS", "AON", "CTAS", "CL", "MCO", "ZTS", "MSI", "PYPL", "NKE", "WMB", "GD", "UPS", "DASH", "CMG", "HCA",
    "PNC", "USB", "HWM", "ECL", "EMR", "ITW", "FTNT", "AZO", "NOC", "JCI", "BK", "REGN", "ADSK", "EOG", "TRV", "ROP", "APD", "NEM", "MAR", "HLT", 
    "AIG", "BSX", "MPC", "CARR", "DXCM", "KDP", "MCHP", "FCX", "PSA", "DLR", "COR", "MET", "TRGP", "T", "TFC", "RSG", "AEP", "VLO", "PCG", "OXY", 
    "PETS", "TEL", "NSC", "OKE", "EIX", "KMB", "ALL", "CMI", "ALLY", "VRSK", "DHI", "SRE", "FDX", "AMP", "F", "GM", "A", "URI", "STZ", "O", "FIS", 
    "KVUE", "PCAR", "DOW", "OTIS", "PEG", "PRU", "GWW", "AME", "BKR", "MNST", "D", "K", "LEN", "DLTR", "ROST", "EXC", "KEYS", "FAST", "CTVA", "CNC",
    "WBD", "SYY", "PAYX", "CTSH", "CSX", "VICI", "IDXX", "KHC", "VRSN", "GEHC", "KR", "RMD", "HAL", "HUM", "GPN", "EBAY", "STT", "HRL", "BBY", "ALGN", 
    "WST", "MTD", "ADM", "FITB", "HPQ", "MTB", "EFX", "WDC", "GLW", "WY", "ZBH", "ED", "SBAC", "DVN", "FTV", "EXR", "HUBB", "WEC", "EQR", "FE", "BRO", 
    "PHM", "ARE", "CDW", "STE", "VMC", "STLD", "LYB", "HIG", "CPT", "CAH", "ES", "DTE", "EXPD", "AVB", "ODFL", "WTW", "TSCO", "NVR", "SW", "RJF", 
    "LUV", "HBAN", "ON", "WAT", "FSLR", "DRI", "MOH", "CBRE", "L", "GL", "TRMB", "RF", "CFG", "KEY", "ATO", "IFF", "INVH", "J", "BALL", "PKG", "CNP", 
    "TYL", "PTC", "SWKS", "LDOS", "TER", "PODD", "COO", "AES", "FICO", "HOLX", "HAS", "CHRW", "MAS", "SNA", "AKAM", "JKHY", "PNR", "IEX", "ALLE", 
    "AOS", "LW", "AMCR", "TAP", "CPB", "SJM", "HSY", "EL", "CLX", "CAG", "CHD", "GEN", "NWS", "RDNT", "FOX", "LYV", "TROW", "BEN", "IVZ", "NTRS", 
    "MKTX", "AIZ", "CINF", "UDR", "HST", "REG", "KIM", "FRT", "MAA", "BXP", "DAY", "RVTY", "TECH", "BIO", "CRL", "TFX", "XRAY", "HSIC", "MRNA", 
    "BIIB", "VTRS", "BAX", "TPR", "RL", "WHR", "NWL", "MHK", "APTV", "BWA", "LKQ", "POOL", "GPC", "ULTA", "DPZ", "YUM", "LVS", "MGM", "WYNN", 
    "RCL", "CCL", "VST", "NI", "PNW", "CMS", "LNT", "AEE", "ETR", "XEL", "SEE", "IP", "MOS", "CF", "NUE", "DD", "PPG", "ALB", "KMI", "FANG", 
    "SM", "APA", "CTRA", "KMX", "AAP", "BBWI", "M", "KSS", "DDS", "URBN", "HOG", "LEG", "MAT", "NCLH", "ALK", "JBL", "FFIV", "UI", "UHS", 
    "ZBRA", "MPWR", "QRVO", "ENPH", "SEDG", "CSIQ", "RUN", "SPWR", "FOXA", "NWSA", "NDAQ", "CBOE", "MSCI", "FACT", "FDS", "TOL", "CZR", "KBH",
    "IRDM", "DECK", "ONON", "CROX", "LULU", "PVH", "VFC", "HBI", "KTB", "UAA", "UA", "CPRI", "COLM", "WSM", "RH", "MNRO", "LES", "FND", "CCI", 
    "GLPI", "RYN", "CUBE", "CHKP", "AAL", "UAL", "STX", "NTAP", "MSTR", "SNOW", "HOOD", "COIN", "RBLX", "NET", "TEAM", "SHOP", "AFRM", "DKNG", 
    "SOFI", "UPST", "U", "DOCU", "ZM", "OKTA", "APP", "DUOL", "PATH", "TWLO", "ROKU", "PINS", "DBX", "SNAP", "SPOT", "GTLB", "MDB", "ZS", "DDOG", 
    "TOST", "GME", "AMC", "PLUG", "CELH", "ELF", "WING", "CHPT", "QS", "LCID", "RIVN", "CVNA", "MARA", "RIOT", "RKLB", "AHH", "ETSY"
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
