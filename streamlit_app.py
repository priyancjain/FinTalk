import streamlit as st
import requests
import json
import os
import torch
from sentence_transformers import SentenceTransformer, util
from typing import List
from pydub import AudioSegment
import subprocess
import streamlit.components.v1 as components

# Initialize embedding model with lazy loading
@st.cache_resource
def get_embedder():
    return SentenceTransformer('all-MiniLM-L6-v2')

# Dummy sample documents (in real case, load from FAISS or DB)
docs = [
    "TSMC beat earnings by 4% due to strong AI chip demand.",
    "Samsung missed earnings by 2% as memory chip prices declined.",
    "Analysts expect Asian tech stocks to remain strong despite volatility."
]

# Streamlit UI setup
st.set_page_config(page_title="Finance Assistant", page_icon="📈")
st.title("🧠 Multi-Agent Market Brief Generator")

# Alpha Vantage API key - you can get a free key from https://www.alphavantage.co/support/#api-key
ALPHA_VANTAGE_API_KEY = "FHY7ZQQK6DKY9A2U"  # Replace with your API key

ticker = st.text_input("Enter Stock Ticker (e.g. TSM, AAPL, MSFT)", value="TSM")

if st.button("📊 Get Market Brief"):
    with st.spinner("Fetching and summarizing market data..."):
        try:
            # --- API Agent Logic ---
            # Get real-time quote
            quote_url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            quote_response = requests.get(quote_url)
            
            # Get company overview
            overview_url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol={ticker}&apikey={ALPHA_VANTAGE_API_KEY}"
            overview_response = requests.get(overview_url)
            
            # Debug information
            st.write(f"Quote API Response Status: {quote_response.status_code}")
            st.write(f"Overview API Response Status: {overview_response.status_code}")
            
            if quote_response.status_code != 200 or overview_response.status_code != 200:
                st.error(f"⚠️ Failed to fetch stock data. Please try again later.")
                st.stop()

            try:
                quote_data = quote_response.json()
                overview_data = overview_response.json()
                
                if "Error Message" in quote_data or "Error Message" in overview_data:
                    st.error(f"⚠️ API Error: {quote_data.get('Error Message', overview_data.get('Error Message', 'Unknown error'))}")
                    st.stop()
                
                quote = quote_data.get('Global Quote', {})
                if not quote:
                    st.error(f"⚠️ No data found for ticker: {ticker}")
                    st.stop()

                stock_data = {
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
                st.error(f"⚠️ Error parsing stock data: {str(e)}")
                st.write("Raw quote response:", quote_response.text)
                st.write("Raw overview response:", overview_response.text)
                st.stop()

            # --- Retrieval Agent Logic ---
            embedder = get_embedder()
            query = f"{ticker} earnings"
            query_embedding = embedder.encode(query, convert_to_tensor=True)
            doc_embeddings = embedder.encode(docs, convert_to_tensor=True)
            hits = util.semantic_search(query_embedding, doc_embeddings, top_k=2)
            top_docs = [docs[hit['corpus_id']] for hit in hits[0]]

            # --- Language Agent Logic ---
            summary = (
                f"Good morning! {stock_data['shortName']} ({ticker}) is currently trading at "
                f"${stock_data['currentPrice']:.2f}, with a market cap of ${stock_data['marketCap']:,.0f}. "
                f"52-week range: ${stock_data['fiftyTwoWeekLow']:.2f} - ${stock_data['fiftyTwoWeekHigh']:.2f}.")
            summary += "\n\n"
            summary += f"Here's what you need to know: {top_docs[0]} Also, {top_docs[1]}"

            # Display result
            st.subheader("📝 Summary")
            st.write(summary)

            # --- Browser-based Speech Synthesis Button ---
            st.subheader("🗣️ Speak Summary (Browser TTS)")
            speak_button = st.button("🔊 Speak Summary")
            if speak_button:
                components.html(f"""
                    <script>
                    var msg = new SpeechSynthesisUtterance({json.dumps(summary)});
                    window.speechSynthesis.speak(msg);
                    </script>
                """, height=0)

        except Exception as e:
            st.error(f"Something went wrong: {str(e)}")
            st.write("Full error details:", str(e))
