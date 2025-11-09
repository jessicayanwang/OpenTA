from pydantic import BaseModel
from typing import List, Optional, Dict
from datetime import datetime
from enum import Enum

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

# Assignment Help models
class AssignmentHelpRequest(BaseModel):
    question: str
    problem_number: Optional[str] = None  # e.g., "Problem 1", "Mario"
    course_id: str = "cs50"
    context: Optional[str] = None  # what the student has tried so far

class AssignmentHelpResponse(BaseModel):
    guidance: str  # Socratic hints and guidance
    concepts: List[str]  # Key concepts to review
    resources: List[str]  # Where to find help
    next_steps: List[str]  # Suggested next steps
    citations: List[Citation]  # Relevant assignment details

# User Role
class UserRole(str, Enum):
    STUDENT = "student"
    PROFESSOR = "professor"

# Auth models
class User(BaseModel):
    user_id: str
    email: str
    role: UserRole
    course_id: str
    name: Optional[str] = None

# Question Clustering models
class QuestionCluster(BaseModel):
    cluster_id: str
    representative_question: str
    similar_questions: List[str]
    count: int
    artifact: Optional[str] = None  # e.g., "Problem Set 1", "Lecture 3"
    section: Optional[str] = None
    canonical_answer_id: Optional[str] = None
    created_at: datetime
    last_seen: datetime

class CanonicalAnswer(BaseModel):
    answer_id: str
    cluster_id: str
    question: str
    answer_markdown: str
    citations: List[Citation]
    created_by: str  # professor user_id
    created_at: datetime
    updated_at: datetime
    is_published: bool = False

class CreateCanonicalAnswerRequest(BaseModel):
    cluster_id: str
    question: str
    answer_markdown: str
    citations: List[Citation]

# Unresolved Queue models
class UnresolvedReason(str, Enum):
    LOW_CONFIDENCE = "low_confidence"
    MISSING_CITATIONS = "missing_citations"
    HINT_ONLY = "hint_only"
    MANUAL_FLAG = "manual_flag"

class UnresolvedItem(BaseModel):
    item_id: str
    student_question: str
    student_id: str
    artifact: Optional[str] = None
    section: Optional[str] = None
    reason: UnresolvedReason
    confidence: Optional[float] = None
    generated_response: Optional[str] = None
    created_at: datetime
    resolved: bool = False
    resolved_by: Optional[str] = None
    resolved_at: Optional[datetime] = None
    linked_canonical_id: Optional[str] = None

class ResolveItemRequest(BaseModel):
    item_id: str
    action: str  # "link" or "create"
    canonical_answer_id: Optional[str] = None  # if linking
    new_answer: Optional[CreateCanonicalAnswerRequest] = None  # if creating

# Confusion Heatmap models
class ConfusionSignal(BaseModel):
    signal_id: str
    student_id: str
    artifact: str  # e.g., "Problem Set 1"
    section: Optional[str] = None
    question: str
    timestamp: datetime
    signal_type: str  # "stuck", "repeated_question", "low_confidence_response"

class ConfusionHeatmapEntry(BaseModel):
    artifact: str
    section: Optional[str] = None
    confusion_count: int
    unique_students: int
    example_questions: List[str]
    last_updated: datetime

# Guardrail Settings models
class GuardrailSettings(BaseModel):
    course_id: str
    max_hints: int = 3  # 1, 3, or 5
    show_thinking_path: bool = True
    graded_banner_text: str = "⚠️ This is a graded assignment. I'll provide hints to guide your learning, not direct answers."
    assignment_rubrics: Dict[str, List[str]] = {}  # assignment_id -> checklist items
    updated_by: str
    updated_at: datetime

class UpdateGuardrailRequest(BaseModel):
    max_hints: Optional[int] = None
    show_thinking_path: Optional[bool] = None
    graded_banner_text: Optional[str] = None
    assignment_rubrics: Optional[Dict[str, List[str]]] = None
