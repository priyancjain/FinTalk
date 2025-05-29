import streamlit as st
import requests
import json
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set Streamlit page config FIRST
st.set_page_config(
    page_title="Finance Assistant",
    page_icon="📈",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.big-title { font-size: 2.5rem; font-weight: 700; color: #2c3e50; }
.user-msg { background: #e3f2fd; border-radius: 8px; padding: 8px 12px; margin-bottom: 4px; }
.assistant-msg { background: #f1f8e9; border-radius: 8px; padding: 8px 12px; margin-bottom: 4px; }
.system-msg { color: #607d8b; font-style: italic; margin-bottom: 4px; }
</style>
""", unsafe_allow_html=True)

# --- Initialize Session State ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- App Setup ---
st.title("Welcome to Finance Assistant")

# --- Sidebar ---
st.sidebar.title("🧠 Finance Assistant")
st.sidebar.markdown("""
**AI-powered, multi-agent market brief generator**

- Real-time stock data  
- News & earnings surprises  
- Conversational UI  
- Voice-ready (browser TTS)

[GitHub](https://github.com/your-repo)
""")

# --- Configuration ---
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
ORCHESTRATOR_URL = "http://localhost:8000/market-brief/"

if not GEMINI_API_KEY:
    st.sidebar.error("GOOGLE_API_KEY not set in environment.")

# --- Helper Functions ---
def extract_tickers_and_sector(prompt, gemini_api_key):
    """
    Uses Gemini to extract stock tickers and sector/region description from a user prompt.
    Returns (tickers: list, sector: str)
    """
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')

    extraction_prompt = (
        "Extract all relevant stock tickers (as a Python list of strings), and a short description of the sector or region, "
        "from the following user prompt. Only include tickers that are relevant to the question. "
        "Return a JSON object with keys 'tickers' and 'sector'.\n\n"
        f"User prompt: {prompt}"
    )

    try:
        response = model.generate_content(extraction_prompt)
        raw = response.text.strip()
        # Remove Markdown code block if present
        if raw.startswith("```"):
            raw = raw.strip("`")
            if "json" in raw:
                raw = raw.split("json")[-1].strip()
        result = json.loads(raw)
        return result.get("tickers", []), result.get("sector", "")
    except Exception as e:
        st.error(f"Gemini extraction error: {e}")
        st.write("Gemini raw output:", response.text)
        return [], ""

# --- Main UI Layout ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Ask a Market Question")
    user_prompt = st.text_input(
        "",
        value="What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?",
        key="user_prompt_input"
    )
    st.caption("e.g. 'What's our risk exposure in Asia tech stocks today, and highlight any earnings surprises?'")
    get_brief = st.button("🔎 Get Market Brief", use_container_width=True)

with col2:
    st.subheader("Conversation History")
    for entry in st.session_state.history:
        if entry["role"] == "user":
            st.markdown(f'<div class="user-msg">🧑 <b>You:</b> {entry["prompt"]}</div>', unsafe_allow_html=True)
        elif entry["role"] == "system":
            st.markdown(f'<div class="system-msg">{entry["content"]}</div>', unsafe_allow_html=True)
        elif entry["role"] == "assistant":
            st.markdown(f'<div class="assistant-msg">🤖 <b>Assistant:</b> {entry["content"]}</div>', unsafe_allow_html=True)

# --- Core Logic ---
if get_brief:
    with st.spinner("Interpreting your question with Gemini..."):
        tickers, sector = extract_tickers_and_sector(user_prompt, gemini_api_key=GEMINI_API_KEY)

        # Update session history
        st.session_state.history.append({
            "role": "user",
            "prompt": user_prompt
        })
        st.session_state.history.append({
            "role": "system",
            "content": f"Extracted tickers: {tickers}<br>Extracted sector/region: {sector}"
        })

        if tickers:
            with st.spinner("Fetching and summarizing market data..."):
                try:
                    response = requests.post(
                        ORCHESTRATOR_URL,
                        json={"tickers": tickers, "sector": sector},
                        timeout=30
                    )
                    response.raise_for_status()
                    result = response.json()
                    summary = result.get("final_summary", "No summary available.")

                    st.session_state.history.append({
                        "role": "assistant",
                        "content": summary
                    })

                    st.success("Market brief generated!")
                    st.subheader("📝 Summary")
                    st.write(summary)

                    if "details" in result:
                        st.subheader("Details (per ticker)")
                        st.write(result["details"])

                except requests.exceptions.RequestException as e:
                    st.error(f"Network error: {str(e)}")
                except json.JSONDecodeError:
                    st.error("Invalid response from orchestrator")
        else:
            st.warning("No tickers extracted from your prompt. Please try a different question.")
