from fastapi import FastAPI, Body
from typing import List, Optional, Dict
import requests
from gtts import gTTS
import os
import tempfile
from pathlib import Path

app = FastAPI()

API_AGENT_URL = "http://localhost:8001/stock-data/"
SCRAPING_AGENT_URL = "http://localhost:8002/earnings-news/"
RETRIEVAL_AGENT_URL = "http://localhost:8003/retrieve/"
LANGUAGE_AGENT_URL = "http://localhost:8005/generate-summary/"

# Create a directory for audio files if it doesn't exist
AUDIO_DIR = Path("audio_files")
AUDIO_DIR.mkdir(exist_ok=True)

@app.get("/ping")
def ping():
    return {"message": "Orchestrator is live!"}

@app.post("/market-brief/")
def market_brief(
    tickers: List[str] = Body(..., embed=True),
    sector: Optional[str] = Body(None, embed=True)
):
    all_results = []
    for ticker in tickers:
        result = {"ticker": ticker}
        try:
            stock_data = requests.get(API_AGENT_URL, params={"ticker": ticker}).json()
            result["stock_data"] = stock_data
        except Exception as e:
            result["stock_data"] = {"error": str(e)}
        try:
            earnings_news = requests.get(SCRAPING_AGENT_URL, params={"ticker": ticker}).json()
            result["earnings_news"] = earnings_news
        except Exception as e:
            result["earnings_news"] = {"error": str(e)}
        try:
            query = f"{ticker} earnings"
            retrieved_context = requests.get(RETRIEVAL_AGENT_URL, params={"query": query, "top_k": 2}).json()
            result["retrieved_context"] = retrieved_context
        except Exception as e:
            result["retrieved_context"] = {"error": str(e)}
        all_results.append(result)

    # Synthesize a combined summary using the language agent
    summary_text = "Failed to generate summary."
    audio_filename = None
    
    try:
        # Format the payload according to the language agent's schema
        for result in all_results:
            ticker = result["ticker"]
            
            # Format stock data
            stock_data = result["stock_data"]
            if "error" in stock_data:
                stock_data = {"error": stock_data["error"]}
            
            # Format earnings news
            earnings_news = result["earnings_news"]
            if "error" in earnings_news:
                earnings_news = {
                    "ticker": ticker,
                    "top_news": []
                }
            elif "top_news" not in earnings_news:
                earnings_news = {
                    "ticker": ticker,
                    "top_news": []
                }
            
            # Format retrieved context
            retrieved_context = result["retrieved_context"]
            if "error" in retrieved_context:
                retrieved_context = {
                    "query": f"{ticker} earnings",
                    "top_k": 2,
                    "results": []
                }
            elif "results" not in retrieved_context:
                retrieved_context = {
                    "query": f"{ticker} earnings",
                    "top_k": 2,
                    "results": []
                }
            
            # Send request to language agent
            payload = {
                "stock_data": stock_data,
                "earnings_news": earnings_news,
                "retrieved_context": retrieved_context
            }
            
            summary_response = requests.post(LANGUAGE_AGENT_URL, json=payload)
            summary_response.raise_for_status()
            summary_json = summary_response.json()
            
            if "summary" in summary_json:
                summary_text = summary_json["summary"]
                break  # Use the first successful summary
            elif "error" in summary_json:
                print(f"Error from language agent for {ticker}: {summary_json['error']}")

        # Generate audio file if we have a valid summary
        if summary_text and summary_text != "Failed to generate summary.":
            try:
                tts = gTTS(text=summary_text, lang='en')
                audio_filename = f"summary_audio_{tickers[0] if tickers else 'all'}.mp3"
                audio_path = AUDIO_DIR / audio_filename
                tts.save(str(audio_path))
            except Exception as e:
                print(f"Error generating audio: {str(e)}")
                audio_filename = None

    except requests.exceptions.RequestException as e:
        summary_text = f"Error communicating with language agent: {str(e)}"
    except Exception as e:
        summary_text = f"Error generating summary: {str(e)}"

    return {
        "tickers": tickers,
        "sector": sector,
        "details": all_results,
        "final_summary": summary_text,
        "audio_file": audio_filename
    }
