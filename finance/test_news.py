from finance.news import get_company_news


if __name__ == "__main__":

    result = get_company_news("NVDA")

    print(result)