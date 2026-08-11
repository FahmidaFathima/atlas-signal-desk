import yfinance as yf


def get_company_news(ticker: str):
    """
    Retrieve recent news specifically associated with a company/ticker.
    Uses yfinance Search rather than Ticker.news because Ticker.news
    can return unrelated Yahoo Finance articles.
    """

    ticker = ticker.upper().strip()

    try:
        search = yf.Search(
            ticker,
            news_count=10,
            raise_errors=True
        )

        raw_news = search.news or []

        if not raw_news:
            return f"No recent news found for {ticker}."

        results = []

        for item in raw_news:
            content = item.get("content", item)

            title = content.get("title") or item.get("title")
            publisher = None

            provider = content.get("provider")

            if isinstance(provider, dict):
                publisher = (
                    provider.get("displayName")
                    or provider.get("name")
                )

            if not publisher:
                publisher = content.get("publisher")

            if not publisher:
                publisher = item.get("publisher")

            link = None

            canonical = content.get("canonicalUrl")

            if isinstance(canonical, dict):
                link = canonical.get("url")

            if not link:
                clickthrough = content.get("clickThroughUrl")

                if isinstance(clickthrough, dict):
                    link = clickthrough.get("url")

            if not link:
                link = item.get("link")

            if not title:
                continue

            # Ignore obviously unrelated/general Yahoo Finance items.
            related = item.get("relatedTickers", [])
            if related and ticker not in [str(x).upper() for x in related]:
                continue

            article = {
                "title": title,
                "publisher": publisher or "Unknown source",
                "link": link or ""
            }

            results.append(article)

            if len(results) >= 5:
                break

        if not results:
            return f"No ticker-specific recent news found for {ticker}."

        output = []

        for article in results:
            line = (
                f"- {article['title']} "
                f"(Source: {article['publisher']})"
            )

            if article["link"]:
                line += f"\n  {article['link']}"

            output.append(line)

        return "\n".join(output)

    except Exception as e:
        return f"Error fetching news for {ticker}: {e}"