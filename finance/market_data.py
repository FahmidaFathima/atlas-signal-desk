import yfinance as yf


def get_stock_data(ticker: str):
    """
    Fetch current market information for a stock.
    """

    ticker = ticker.upper().strip()

    try:
        stock = yf.Ticker(ticker)

        info = stock.info

        price = (
            info.get("currentPrice")
            or info.get("regularMarketPrice")
        )

        previous_close = info.get(
            "previousClose"
        )

        market_cap = info.get(
            "marketCap"
        )

        currency = info.get(
            "currency",
            "USD"
        )

        company_name = info.get(
            "longName",
            ticker
        )

        sector = info.get(
            "sector",
            "Unknown"
        )

        industry = info.get(
            "industry",
            "Unknown"
        )

        return {
            "ticker": ticker,
            "company": company_name,
            "price": price,
            "previous_close": previous_close,
            "market_cap": market_cap,
            "currency": currency,
            "sector": sector,
            "industry": industry,
        }

    except Exception as error:

        return {
            "error": str(error),
            "ticker": ticker
        }