from pydantic import BaseModel
from typing import List, Optional, Dict

class NewsItem(BaseModel):
    title: str
    url: Optional[str] = None
    summary: Optional[str] = None

class EarningsNews(BaseModel):
    ticker: str
    top_news: List[NewsItem]

class RetrievedContext(BaseModel):
    query: str
    top_k: int
    results: List[str]

class LanguageRequest(BaseModel):
    stock_data: Dict
    earnings_news: EarningsNews
    retrieved_context: RetrievedContext
