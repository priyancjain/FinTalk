from fastapi import FastAPI, Query
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()
ALPHA_VANTAGE_KEY = os.getenv("ALPHA_VANTAGE_KEY")

if not ALPHA_VANTAGE_KEY:
    raise ValueError("ALPHA_VANTAGE_KEY environment variable is not set")

@app.get("/ping")
def ping():
    return {"message": "API Agent is up and running!"}

@app.get("/stock-data/")
def get_stock_data(ticker: str = Query(..., description="e.g., TSM, 005930.KQ")):
    try:
        # Get real-time quote
        quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
        quote_response = requests.get(quote_url)
        quote_data = quote_response.json()

        # Check for API errors
        if "Error Message" in quote_data:
            return {"error": f"Alpha Vantage API error: {quote_data['Error Message']}"}
        if "Note" in quote_data:
            return {"error": f"Alpha Vantage API note: {quote_data['Note']}"}

        # Get company overview
        overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_KEY}"
        overview_response = requests.get(overview_url)
        overview_data = overview_response.json()

        # Check for API errors in overview
        if "Error Message" in overview_data:
            return {"error": f"Alpha Vantage API error: {overview_data['Error Message']}"}
        if "Note" in overview_data:
            return {"error": f"Alpha Vantage API note: {overview_data['Note']}"}

        quote = quote_data.get('Global Quote', {})
        if not quote:
            return {"error": f"No data found for ticker: {ticker}"}

        return {
            "ticker": ticker,
            "shortName": overview_data.get("Name", "Unknown"),
            "currentPrice": float(quote.get("05. price", 0)),
            "marketCap": float(overview_data.get("MarketCapitalization", 0)),
            "fiftyTwoWeekHigh": float(overview_data.get("52WeekHigh", 0)),
            "fiftyTwoWeekLow": float(overview_data.get("52WeekLow", 0)),
            "previousClose": float(quote.get("08. previous close", 0)),
            "open": float(quote.get("02. open", 0)),
        }
    except Exception as e:
        return {"error": str(e)}
