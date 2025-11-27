"""
Pydantic models for adaptive learning endpoints
"""
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PopQuizItemResponse(BaseModel):
    question_id: str
    topic: str
    subtopic: str
    question: str
    options: List[str]
    difficulty: float
    source_citation: str

class DailyQuizResponse(BaseModel):
    date: str
    items: List[PopQuizItemResponse]
    mastery_summary: dict  # topic -> mastery_score

class SubmitAnswerRequest(BaseModel):
    student_id: str
    question_id: str
    selected_index: int
    response_time_seconds: float

class SubmitAnswerResponse(BaseModel):
    correct: bool
    correct_answer: str
    explanation: str
    next_review: Optional[str]
    mastery_update: dict

class InterventionCheckResponse(BaseModel):
    offer: bool
    type: Optional[str] = None
    reason: Optional[str] = None
    signals: Optional[List[str]] = None
    suggested_action: Optional[str] = None

class ConceptCheckRequest(BaseModel):
    student_id: str
    topic: str
    num_items: int = 2

class ExamRunwayRequest(BaseModel):
    student_id: str
    exam_date: str  # ISO format
    exam_type: str  # "midterm" or "final"
    hours_per_day: float = 3.0
    course_id: str = "cs50"

class DailyTargetResponse(BaseModel):
    day_number: int
    date: str
    focus_topics: List[str]
    time_blocks: List[dict]
    gap_check_items: int
    intensity: str

class ExamRunwayResponse(BaseModel):
    exam_type: str
    exam_date: str
    days_until_exam: int
    daily_targets: List[DailyTargetResponse]
    priority_topics: List[str]
    total_hours_allocated: float

class MockExamResponse(BaseModel):
    exam_type: str
    num_questions: int
    time_limit_minutes: int
    questions: List[PopQuizItemResponse]

class MasteryStatusResponse(BaseModel):
    student_id: str
    topics: List[dict]  # [{topic, mastery_score, confidence, attempts}]
    weak_topics: List[str]
    strong_topics: List[str]
    overall_progress: float

class BehaviorSessionRequest(BaseModel):
    session_id: str
    student_id: str
    topic: str

class BehaviorLogRequest(BaseModel):
    session_id: str
    event_type: str  # "hint", "question", "error", "copy_paste"
    data: Optional[dict] = None
