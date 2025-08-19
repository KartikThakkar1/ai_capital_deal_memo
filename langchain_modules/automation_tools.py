# this file has code for fetching stock data from an external source (yahoo finance) for a given stock ticker

import yfinance as yf

def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        return {
            "name": info.get("shortName"),
            "industry": info.get("industry"),
            "sector": info.get("sector"),
            "market_cap": info.get("marketCap"),
            "current_price": info.get("currentPrice"),
            "pe_ratio": info.get("trailingPE"),
            "beta": info.get("beta"),
            "forward_pe": info.get("forwardPE"),
            "summary": info.get("longBusinessSummary"),
        }
    except Exception as e:
        return {"error": f"Failed to fetch stock data: {str(e)}"}
