from pydantic import BaseModel
from typing import List, Optional

class ChatRequest(BaseModel):
    question: str
    course_id: str = "cs50"

class Citation(BaseModel):
    source: str
    section: str
    text: str
    relevance_score: float

class ChatResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float
