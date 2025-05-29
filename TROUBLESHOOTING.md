# Finance Assistant - Troubleshooting Guide

## Technology Stack

### Core Technologies
- **Python 3.11+**: Main programming language
- **FastAPI**: Backend framework for microservices
- **Streamlit**: Frontend UI framework
- **Uvicorn**: ASGI server for FastAPI applications
- **tmux**: Terminal multiplexer for running multiple services

### AI/ML Components
- **Google Gemini API**: For natural language processing and summary generation
- **gTTS (Google Text-to-Speech)**: For converting summaries to speech
- **sentence-transformers**: For semantic search and context retrieval
- **FAISS**: Vector database for efficient similarity search

### External APIs
- **Alpha Vantage**: For real-time stock data and news
- **Google AI Studio**: For Gemini API access

## Common Errors and Solutions

### 1. API Key Issues
```python
ValueError: ALPHA_VANTAGE_KEY environment variable is not set
ValueError: GOOGLE_API_KEY not found in open.env
```
**Solution:**
- Create a `.env` file in the project root with:
  ```
  ALPHA_VANTAGE_KEY=your_alpha_vantage_key_here
  GOOGLE_API_KEY=your_google_api_key_here
  ```
- For language agent, ensure `open.env` exists in `backend/agents/language_agent/`
- Get API keys from:
  - Alpha Vantage: https://www.alphavantage.co/support/#api-key
  - Google AI Studio: https://makersuite.google.com/app/apikey

### 2. Service Connection Issues
```python
Error: Connection aborted, RemoteDisconnected('Remote end closed connection without response')
```
**Solution:**
- Ensure all services are running using `./run_services.sh`
- Check service health:
  ```bash
  curl http://localhost:8000/ping  # Orchestrator
  curl http://localhost:8001/ping  # API Agent
  curl http://localhost:8002/ping  # Scraping Agent
  curl http://localhost:8003/ping  # Retrieval Agent
  curl http://localhost:8005/ping  # Language Agent
  ```
- Verify ports are not in use:
  ```bash
  lsof -i :8000-8005
  ```

### 3. Alpha Vantage API Rate Limits
```python
"error": "No news found or API limit exceeded."
"error": "Alpha Vantage API note: Thank you for using Alpha Vantage! Our standard API call frequency is 5 calls per minute and 500 calls per day."
```
**Solution:**
- Use a paid API key for higher limits
- Implement request caching
- Add delays between requests
- Handle rate limit errors gracefully in the UI

### 4. Language Agent 422 Errors
```python
422 Client Error: Unprocessable Entity for url: http://localhost:8005/generate-summary/
```
**Solution:**
- Ensure payload matches the expected schema:
  ```python
  {
    "stock_data": Dict,
    "earnings_news": {
      "ticker": str,
      "top_news": List[NewsItem]
    },
    "retrieved_context": {
      "query": str,
      "top_k": int,
      "results": List[str]
    }
  }
  ```
- Check data formatting in orchestrator
- Validate input data before sending to language agent

### 5. Text-to-Speech Issues
```python
'fp' is not a file-like object or it does not take bytes: 'dict' object has no attribute 'strip'
```
**Solution:**
- Ensure summary text is a string, not a dictionary
- Create audio directory if it doesn't exist
- Handle TTS errors gracefully
- Check file permissions for audio directory

### 6. Service Startup Issues
```bash
tmux is not installed
```
**Solution:**
- Install tmux:
  ```bash
  # macOS
  brew install tmux
  
  # Ubuntu/Debian
  sudo apt-get install tmux
  ```
- Alternative: Run services manually in separate terminals

## Development Tips

### Running Services
1. **Using tmux (Recommended):**
   ```bash
   ./run_services.sh
   ```
   - Use `Ctrl+b d` to detach
   - Use `Ctrl+b n` to switch windows
   - Use `tmux attach -t finance_assistant` to reattach

2. **Manual Start:**
   ```bash
   # Terminal 1
   uvicorn backend.orchestrator.main:app --reload --port 8000
   
   # Terminal 2
   uvicorn backend.agents.api_agent.main:app --reload --port 8001
   
   # Terminal 3
   uvicorn backend.agents.scraping_agent.main:app --reload --port 8002
   
   # Terminal 4
   uvicorn backend.agents.retrieval_agent.main:app --reload --port 8003
   
   # Terminal 5
   uvicorn backend.agents.language_agent.main:app --reload --port 8005
   
   # Terminal 6
   streamlit run streamlit_app.py
   ```

### Debugging
1. **Check Logs:**
   - Each service outputs logs to its terminal
   - Use `Ctrl+b [window_number]` to switch to specific service
   - Check for error messages in red

2. **API Testing:**
   ```bash
   # Test orchestrator
   curl -X POST http://localhost:8000/market-brief/ \
     -H "Content-Type: application/json" \
     -d '{"tickers": ["AAPL"], "sector": "Technology"}'
   ```

3. **Environment Variables:**
   - Use `print(os.environ)` in services to debug
   - Check `.env` file permissions
   - Verify variable names match exactly

### Performance Optimization
1. **API Rate Limits:**
   - Implement caching for stock data
   - Batch requests when possible
   - Use websockets for real-time updates

2. **Memory Usage:**
   - Monitor FAISS index size
   - Clear old audio files periodically
   - Use connection pooling for database

## Contributing
When adding new features or fixing bugs:
1. Document any new errors encountered
2. Update this troubleshooting guide
3. Add appropriate error handling
4. Include test cases for new functionality

## Support
For additional help:
1. Check the main README.md
2. Review API documentation:
   - [Alpha Vantage API](https://www.alphavantage.co/documentation/)
   - [Google Gemini API](https://ai.google.dev/docs)
3. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Environment details
   - Relevant logs 