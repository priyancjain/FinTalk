from fastapi import FastAPI, Query
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
ALPHA_VANTAGE_KEY = os.getenv("3XSOHH3BSRQABXRZ")

@app.get("/ping")
def ping():
    return {"message": "Scraping Agent with Alpha Vantage is running!"}

@app.get("/earnings-news/")
def get_news(ticker: str = Query(..., description="Stock ticker like AAPL, TSM")):
    try:
        url = (
            f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}"
            f"&apikey={ALPHA_VANTAGE_KEY}"
        )

        response = requests.get(url)
        data = response.json()

        if "feed" not in data:
            return {"error": "No news found or API limit exceeded."}

        
        top_news = [
            {
                "title": item["title"],
                "url": item["url"],
                "summary": item["summary"]
            }
            for item in data["feed"][:3]
        ]

        return {
            "ticker": ticker,
            "top_news": top_news
        }

    except Exception as e:
        return {"error": str(e)}