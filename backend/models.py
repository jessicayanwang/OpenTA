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

# Study Plan models
class StudyPlanRequest(BaseModel):
    course_id: str = "cs50"
    goal_scope: str  # e.g., "term", "midterm", "final"
    hours_per_week: int
    current_level: str  # e.g., "beginner", "intermediate", "advanced"
    duration_weeks: Optional[int] = None  # required for term plans; optional for exam-focused
    exam_in_weeks: Optional[int] = None  # optional for midterm/final plans
    focus_topics: Optional[List[str]] = None  # topics the user wants to emphasize
    constraints: Optional[List[str]] = None  # e.g., "no weekends", "only evenings"
    notes: Optional[str] = None

class StudyTask(BaseModel):
    day: str
    focus: str
    duration_hours: float
    resources: Optional[List[str]] = None

class WeekPlan(BaseModel):
    week_number: int
    objectives: List[str]
    tasks: List[StudyTask]

class StudyPlanResponse(BaseModel):
    title: str
    summary: str
    hours_per_week: int
    duration_weeks: int
    weekly_plan: List[WeekPlan]
    tips: List[str]
