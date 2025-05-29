from fastapi import FastAPI
import google.generativeai as genai
from dotenv import dotenv_values
from pathlib import Path
from .schemas import LanguageRequest

# Load environment variables
env_path = Path(__file__).parent / "open.env"
env_vars = dotenv_values(env_path)
GOOGLE_API_KEY = env_vars.get("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError(f"GOOGLE_API_KEY not found in {env_path}. Please check the file content.")

# Configure Gemini
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash')

app = FastAPI()

@app.get("/ping")
def ping():
    return {"message": "Language Agent is working!"}

@app.post("/generate-summary/")
def generate_summary(payload: LanguageRequest):
    try:
        stock_data = payload.stock_data
        news = payload.earnings_news.top_news
        context = payload.retrieved_context.results

        news_text = "\n".join([f"- {item.title}" for item in news]) if news else "No headlines available."
        context_text = "\n".join(context) if context else "No extra context available."

        prompt = f"""
You are a financial assistant for a portfolio manager. Based on the following data, generate a short spoken-style market brief, make it sound interesting (2 or 3 sentences):

📊 Stock Info:
{stock_data}

📰 Earnings Headlines:
{news_text}

📚 Context:
{context_text}
"""

        print("🔎 Prompt to Gemini:")
        print(prompt)

        # Generate response using Gemini
        response = model.generate_content(
            prompt,
            generation_config={
                'temperature': 0.4,
                'top_p': 0.8,
                'top_k': 40,
            }
        )

        print("Gemini response:", response.text)
        return {"summary": response.text}

    except Exception as e:
        print("Error in /generate-summary/:", str(e))
        return {"error": str(e)}
