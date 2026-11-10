from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class ChatRequest(BaseModel):
    session_id: str
    message: str
    timezone: str = "UTC"


class MessageOut(BaseModel):
    id: int
    session_id: str
    role: str
    content: str
    sources: list[str] = []
    created_at: datetime


class SourceOut(BaseModel):
    title: str
    url: str
    snippet: str


class SearchResult(BaseModel):
    title: str
    url: str
    snippet: str


class WebSearchInput(BaseModel):
    query: str
