"""
OpenTA Backend - Multi-Agent Framework
FastAPI Application with Orchestrator
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import uuid
from datetime import datetime

from models import (
    ChatRequest, ChatResponse, StudyPlanRequest, StudyPlanResponse, 
    AssignmentHelpRequest, AssignmentHelpResponse,
    QuestionCluster, CanonicalAnswer, CreateCanonicalAnswerRequest,
    UnresolvedItem, ResolveItemRequest, ConfusionHeatmapEntry,
    GuardrailSettings, UpdateGuardrailRequest,
    DiagnosticQuestion, DiagnosticResponse, DiagnosticResult,
)
from models_adaptive import (
    PopQuizItemResponse, DailyQuizResponse, SubmitAnswerRequest, SubmitAnswerResponse,
    InterventionCheckResponse, ConceptCheckRequest, ExamRunwayRequest, 
    ExamRunwayResponse, MockExamResponse, MasteryStatusResponse,
    BehaviorSessionRequest, BehaviorLogRequest
)
from document_store import DocumentStore
from retrieval import HybridRetriever
from professor_service import ProfessorService
from typing import List

# Multi-Agent Framework Imports
from agents.orchestrator import OrchestratorAgent
from agents.qa_agent import QAAgent
from agents.assignment_helper_agent import AssignmentHelperAgent
from agents.study_plan_agent import StudyPlanAgent
from memory.shared_memory import SharedMemory
from tools.retrieval_tool import RetrievalTool
from tools.citation_tool import CitationTool
from tools.analytics_tool import AnalyticsTool
from tools.guardrail_tool import GuardrailTool
from tools.openai_tool import OpenAITool
from protocols.agent_message import AgentMessage, MessageType
import os
from dotenv import load_dotenv
# from diagnostic_service import DiagnosticService
# from learning_flow_service import LearningFlowService

# Adaptive Learning Imports
from adaptive.spaced_repetition import SpacedRepetitionEngine, ReviewResult
from adaptive.pop_quiz_service import PopQuizService
from adaptive.behavioral_tracker import BehavioralTracker
from adaptive.exam_runway import ExamRunwayService
from adaptive.reminder_service import ReminderService

# Load environment variables
load_dotenv()

app = FastAPI(title="OpenTA API - Multi-Agent", version="0.2.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_store = DocumentStore()
retriever = None
professor_service = None  # Will be initialized with embedder in startup

# Multi-Agent Framework
shared_memory = SharedMemory()
orchestrator = None
study_plan_agent = None
# diagnostic_service = None
# learning_flow_service = None

# Adaptive Learning Components
spaced_rep_engine = None
pop_quiz_service = None
behavioral_tracker = None
exam_runway_service = None
reminder_service = None

@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent system on startup"""
    global retriever, orchestrator, professor_service, study_plan_agent
    global spaced_rep_engine, pop_quiz_service, behavioral_tracker, exam_runway_service, reminder_service
    
    print("🚀 Starting OpenTA Multi-Agent System...")
    
    # Load course documents
    data_dir = Path(__file__).parent / "data"
    
    print("📚 Loading course documents...")
    for file_path in data_dir.glob("*.txt"):
        print(f"  - Loading {file_path.name}")
        with open(file_path, 'r') as f:
            content = f.read()
            document_store.ingest_document(content, file_path.name)
    
    print(f"✅ Loaded {len(document_store.chunks)} document chunks")
    
    # Initialize retriever and index chunks
    retriever = HybridRetriever()
    retriever.index_chunks(document_store.get_all_chunks())
    
    # Initialize professor service with embedder for semantic clustering
    professor_service = ProfessorService(embedder=retriever.embedder)
    # Initialize study plan agent (also reused for diagnostics follow-ups)
    study_plan_agent = StudyPlanAgent()
    # diagnostic_data_path = data_dir / "cs50_initial_diagnostic.json"
    # diagnostic_service = DiagnosticService(diagnostic_data_path, study_plan_agent)
    # learning_flow_service = LearningFlowService(diagnostic_service)
    
    # Initialize tools
    retrieval_tool = RetrievalTool(retriever)
    citation_tool = CitationTool()
    analytics_tool = AnalyticsTool(professor_service)
    guardrail_tool = GuardrailTool(professor_service)
    
    # Initialize OpenAI tool (will use API key from environment)
    try:
        openai_tool = OpenAITool()
        print("✅ OpenAI integration enabled")
    except ValueError as e:
        print(f"⚠️  OpenAI not available: {str(e)}")
        print("   System will use rule-based answer generation")
        openai_tool = None
    
    # Initialize orchestrator
    orchestrator = OrchestratorAgent(shared_memory)
    
    # Initialize and register agents
    qa_agent = QAAgent()
    qa_agent.register_tool(retrieval_tool)
    qa_agent.register_tool(citation_tool)
    qa_agent.register_tool(analytics_tool)
    if openai_tool:
        qa_agent.register_tool(openai_tool)
    orchestrator.register_agent(qa_agent)
    
    # Initialize behavioral tracker first (will be used by assignment helper)
    behavioral_tracker = BehavioralTracker()
    
    assignment_helper = AssignmentHelperAgent(behavioral_tracker=behavioral_tracker)
    assignment_helper.register_tool(retrieval_tool)
    assignment_helper.register_tool(citation_tool)
    assignment_helper.register_tool(analytics_tool)
    assignment_helper.register_tool(guardrail_tool)
    orchestrator.register_agent(assignment_helper)
    
    study_plan_agent = StudyPlanAgent()
    orchestrator.register_agent(study_plan_agent)
    
    # Initialize Adaptive Learning System
    print("\n🧠 Initializing Adaptive Learning System...")
    spaced_rep_engine = SpacedRepetitionEngine()
    pop_quiz_service = PopQuizService(document_store, retriever, spaced_rep_engine)
    # behavioral_tracker already initialized above for assignment helper
    exam_runway_service = ExamRunwayService(spaced_rep_engine)
    reminder_service = ReminderService()
    print("✅ Adaptive Learning Ready!")
    print(f"   - Spaced Repetition Engine")
    print(f"   - Pop Quiz Service ({len(pop_quiz_service.question_bank)} topics)")
    print(f"   - Behavioral Tracker (integrated with Assignment Helper)")
    print(f"   - Exam Runway Service")
    print(f"   - Reminder Service (email {'enabled' if reminder_service.email_enabled else 'disabled'})")
    
    print("\n✅ Multi-Agent System Ready!")
    print(f"   Registered agents: {len(orchestrator.agents)}")
    for agent_id, agent in orchestrator.agents.items():
        print(f"   - {agent.name} ({agent_id})")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpenTA API - Multi-Agent Framework",
        "version": "0.2.0",
        "status": "running",
        "framework": "multi-agent"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    agent_status = orchestrator.get_agent_status() if orchestrator else {}
    return {
        "status": "healthy",
        "chunks_indexed": len(document_store.chunks) if document_store else 0,
        "agents": agent_status
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, student_id: str = "student1"):
    """
    Main chat endpoint - routes through orchestrator
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    print(f"\n❓ Question: {request.question}")
    
    # First, check if there's a canonical answer for this question
    canonical_answer = professor_service.find_canonical_answer(request.question, similarity_threshold=0.75)
    
    if canonical_answer:
        print(f"✅ Found canonical answer (professor-verified)")
        # Return the canonical answer with high confidence
        return ChatResponse(
            answer=f"**[Professor-Verified Answer]**\n\n{canonical_answer.answer_text}",
            citations=canonical_answer.citations,
            confidence=0.95,  # High confidence for professor-created answers
            suggested_questions=[]
        )
    
    # No canonical answer found, proceed with normal agent processing
    # Create agent message
    message = AgentMessage(
        message_id=str(uuid.uuid4()),
        sender="user",
        receiver="orchestrator",
        message_type=MessageType.REQUEST,
        content={
            'question': request.question,
            'student_id': student_id,
            'course_id': request.course_id,
            'type': 'qa'
        },
        context={},
        priority=3,
        timestamp=datetime.now()
    )
    
    # Process through orchestrator
    response = await orchestrator.process(message)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    # Extract chat response
    chat_response_data = response.data.get('chat_response', {})
    chat_response = ChatResponse(**chat_response_data)
    
    print(f"✅ Answer generated (confidence: {chat_response.confidence:.2f})")
    
    return chat_response

@app.post("/api/study-plan", response_model=StudyPlanResponse)
async def study_plan(request: StudyPlanRequest, student_id: str = "student1"):
    """
    Generate a personalized study plan through orchestrator
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")

    print(f"\n🗓️ Study Plan request: scope={request.goal_scope}, hours/week={request.hours_per_week}")
    
    # Create agent message
    message = AgentMessage(
        message_id=str(uuid.uuid4()),
        sender="user",
        receiver="orchestrator",
        message_type=MessageType.REQUEST,
        content={
            'student_id': student_id,
            'goal_scope': request.goal_scope,
            'hours_per_week': request.hours_per_week,
            'current_level': request.current_level,
            'duration_weeks': request.duration_weeks,
            'exam_in_weeks': request.exam_in_weeks,
            'focus_topics': request.focus_topics,
            'constraints': request.constraints,
            'type': 'study_plan'
        },
        context={},
        priority=3,
        timestamp=datetime.now()
    )
    
    # Process through orchestrator
    response = await orchestrator.process(message)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    # Extract study plan
    plan_data = response.data.get('study_plan', {})
    plan = StudyPlanResponse(**plan_data)
    
    print(f"✅ Study plan generated: {plan.duration_weeks} weeks, {plan.hours_per_week} hrs/week")
    return plan

# Old diagnostic endpoints - replaced by new adaptive system
# @app.get("/api/diagnostic", response_model=List[DiagnosticQuestion])
# async def get_diagnostic(course_id: str = "cs50"):
#     """Return professor-seeded diagnostic questions for onboarding."""
#     if not diagnostic_service:
#         raise HTTPException(status_code=503, detail="Diagnostic service not initialized")
#     return diagnostic_service.get_questions(course_id)

# @app.post("/api/diagnostic/submit", response_model=DiagnosticResult)
# async def submit_diagnostic(request: DiagnosticResponse):
#     """Score diagnostic responses, cluster weak topics, and return an annotated first-week plan."""
#     if not diagnostic_service:
#         raise HTTPException(status_code=503, detail="Diagnostic service not initialized")
#     return diagnostic_service.score_and_plan(request)

# Old endpoints - replaced by new adaptive learning system
# @app.get("/api/pop-quiz")
# async def pop_quiz(course_id: str = "cs50", count: int = 4):
#     """Spaced pop quiz items sourced only from course materials."""
#     if not learning_flow_service:
#         raise HTTPException(status_code=503, detail="Learning flow service not initialized")
#     return learning_flow_service.spaced_pop_quiz(course_id, count)
# 
# @app.get("/api/exam/runway")
# async def exam_runway(course_id: str = "cs50", days_to_exam: int = 7):
#     """Exam runway CTA with a compact gap check derived from in-scope materials."""
#     if not learning_flow_service:
#         raise HTTPException(status_code=503, detail="Learning flow service not initialized")
#     return learning_flow_service.exam_runway(course_id, days_to_exam)
# 
# @app.get("/api/assignment/concept-check")
# async def assignment_concept_check(course_id: str = "cs50", pset: str = "pset1", hint_count: int = 2):
#     """Assignment-period micro-adaptivity: two-item concept check when hints/dwell spike."""
#     if not learning_flow_service:
#         raise HTTPException(status_code=503, detail="Learning flow service not initialized")
#     return learning_flow_service.assignment_concept_check(course_id, pset, hint_count)

@app.get("/api/faq")
async def get_faq(course_id: str = "cs50"):
    """Get all published canonical answers for FAQ page"""
    answers = professor_service.get_all_published_canonical_answers()
    
    # Format for frontend
    faq_items = []
    for answer in answers:
        # Find the cluster to get representative question
        representative_question = "General Question"
        for cluster in professor_service.clusters.values():
            if cluster.canonical_answer_id == answer.answer_id:
                representative_question = cluster.representative_question
                break
        
        faq_items.append({
            "question": representative_question,
            "answer": answer.answer_text,
            "created_at": answer.created_at.isoformat(),
            "created_by": answer.created_by
        })
    
    return {"faq": faq_items}

@app.post("/api/assignment-help", response_model=AssignmentHelpResponse)
async def assignment_help(request: AssignmentHelpRequest, student_id: str = "student1"):
    """
    Help students with assignments using Socratic method through orchestrator
    """
    if not orchestrator:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    print(f"\n📝 Assignment help request: {request.question}")
    if request.problem_number:
        print(f"   Problem: {request.problem_number}")
    
    # Create agent message
    message = AgentMessage(
        message_id=str(uuid.uuid4()),
        sender="user",
        receiver="orchestrator",
        message_type=MessageType.REQUEST,
        content={
            'question': request.question,
            'problem_number': request.problem_number,
            'student_id': student_id,
            'course_id': request.course_id,
            'context': request.context,
            'type': 'assignment_help'
        },
        context={},
        priority=3,
        timestamp=datetime.now()
    )
    
    # Process through orchestrator
    response = await orchestrator.process(message)
    
    if not response.success:
        raise HTTPException(status_code=500, detail=response.error)
    
    # Extract help response
    help_data = response.data.get('help_response', {})
    help_response = AssignmentHelpResponse(**help_data)
    print(f"✅ Guidance generated with {len(help_response.concepts)} key concepts")
    
    return help_response

# ========== PROFESSOR CONSOLE ENDPOINTS ==========

@app.get("/api/professor/dashboard")
async def get_dashboard_metrics(course_id: str = "cs50", days: int = 7):
    """Get dashboard overview metrics"""
    from datetime import datetime, timedelta
    from mock_data_generator import MockDataGenerator
    
    cutoff = datetime.now() - timedelta(days=days)
    recent_questions = [q for q in professor_service.question_logs if q["timestamp"] >= cutoff]
    
    # Calculate metrics
    total_questions = len(recent_questions)
    avg_confidence = sum(q["confidence"] for q in recent_questions) / max(len(recent_questions), 1)
    
    # Count struggling students (3+ confusion signals)
    student_confusion_count = {}
    for signal in professor_service.confusion_signals:
        if signal.timestamp >= cutoff:
            student_id = signal.student_id
            student_confusion_count[student_id] = student_confusion_count.get(student_id, 0) + 1
    
    struggling_students = len([s for s, count in student_confusion_count.items() if count >= 3])
    
    # Unresolved count
    unresolved_count = len([item for item in professor_service.unresolved_queue.values() if not item.resolved])
    
    # Top confusion topics
    topic_confusion = {}
    for signal in professor_service.confusion_signals:
        if signal.timestamp >= cutoff:
            topic = signal.section or signal.artifact
            topic_confusion[topic] = topic_confusion.get(topic, 0) + 1
    
    top_topics = sorted(topic_confusion.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Recent activity (last 10 questions)
    recent_activity = sorted(recent_questions, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    return {
        "metrics": {
            "total_questions": total_questions,
            "avg_confidence": round(avg_confidence, 2),
            "struggling_students": struggling_students,
            "unresolved_items": unresolved_count
        },
        "top_confusion_topics": [{"topic": topic, "count": count} for topic, count in top_topics],
        "recent_activity": [
            {
                "question": q["question"],
                "student_id": q["student_id"],
                "confidence": q["confidence"],
                "timestamp": q["timestamp"].isoformat(),
                "artifact": q.get("artifact", "Unknown")
            }
            for q in recent_activity
        ]
    }

@app.get("/api/professor/students")
async def get_student_analytics(course_id: str = "cs50"):
    """Get student analytics"""
    from datetime import datetime, timedelta
    
    # Analyze each student
    students = {}
    
    # Collect data per student
    for q in professor_service.question_logs:
        student_id = q["student_id"]
        if student_id not in students:
            students[student_id] = {
                "student_id": student_id,
                "questions_asked": 0,
                "avg_confidence": 0,
                "confusion_signals": 0,
                "last_active": None,
                "topics": set()
            }
        
        students[student_id]["questions_asked"] += 1
        students[student_id]["topics"].add(q.get("section", "Unknown"))
        
        if students[student_id]["last_active"] is None or q["timestamp"] > students[student_id]["last_active"]:
            students[student_id]["last_active"] = q["timestamp"]
    
    # Count confusion signals
    for signal in professor_service.confusion_signals:
        student_id = signal.student_id
        if student_id in students:
            students[student_id]["confusion_signals"] += 1
    
    # Calculate avg confidence
    for student_id in students:
        student_questions = [q for q in professor_service.question_logs if q["student_id"] == student_id]
        if student_questions:
            students[student_id]["avg_confidence"] = sum(q["confidence"] for q in student_questions) / len(student_questions)
    
    # Categorize students
    for student in students.values():
        student["topics"] = list(student["topics"])
        student["last_active"] = student["last_active"].isoformat() if student["last_active"] else None
        
        # Determine status
        if student["confusion_signals"] >= 3:
            student["status"] = "struggling"
        elif student["questions_asked"] == 0:
            student["status"] = "silent"
        elif student["avg_confidence"] > 0.8:
            student["status"] = "thriving"
        else:
            student["status"] = "active"
    
    return {"students": list(students.values())}

@app.get("/api/professor/content-gaps")
async def get_content_gaps(course_id: str = "cs50"):
    """Identify content gaps"""
    from mock_data_generator import MockDataGenerator
    
    generator = MockDataGenerator(professor_service)
    gaps = generator.generate_content_gaps()
    
    return {"gaps": gaps}

@app.post("/api/professor/seed-demo-data")
async def seed_demo_data():
    """Seed system with demo data"""
    from mock_data_generator import seed_demo_data
    
    generator = seed_demo_data(professor_service)
    
    return {
        "success": True,
        "message": "Demo data generated",
        "stats": {
            "questions": len(professor_service.question_logs),
            "clusters": len(professor_service.clusters),
            "students": len(generator.get_student_personas())
        }
    }

@app.get("/api/professor/clusters", response_model=List[QuestionCluster])
async def get_question_clusters(course_id: str = "cs50", min_count: int = 2, semantic: bool = True):
    """Get question clusters for professor review"""
    if semantic:
        # Use semantic clustering with embeddings
        return professor_service.get_semantic_clusters(course_id, similarity_threshold=0.7, min_count=min_count)
    else:
        # Use simple keyword-based clustering
        return professor_service.get_question_clusters(course_id, min_count)

@app.post("/api/professor/canonical-answer", response_model=CanonicalAnswer)
async def create_canonical_answer(request: CreateCanonicalAnswerRequest, professor_id: str = "prof1"):
    """Create a canonical answer for a question cluster"""
    return professor_service.create_canonical_answer(request, professor_id)

@app.post("/api/professor/canonical-answer/{answer_id}/publish", response_model=CanonicalAnswer)
async def publish_canonical_answer(answer_id: str):
    """Publish a canonical answer"""
    try:
        return professor_service.publish_canonical_answer(answer_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/professor/unresolved", response_model=List[UnresolvedItem])
async def get_unresolved_queue(course_id: str = "cs50"):
    """Get unresolved queue items"""
    return professor_service.get_unresolved_queue(course_id)

@app.post("/api/professor/resolve", response_model=UnresolvedItem)
async def resolve_item(request: ResolveItemRequest, professor_id: str = "prof1"):
    """Resolve an unresolved queue item"""
    try:
        return professor_service.resolve_item(request, professor_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/api/professor/confusion-heatmap", response_model=List[ConfusionHeatmapEntry])
async def get_confusion_heatmap(course_id: str = "cs50", days: int = 7):
    """Get confusion heatmap"""
    return professor_service.get_confusion_heatmap(course_id, days)

@app.get("/api/professor/guardrails", response_model=GuardrailSettings)
async def get_guardrail_settings(course_id: str = "cs50"):
    """Get guardrail settings"""
    return professor_service.get_guardrail_settings(course_id)

@app.put("/api/professor/guardrails", response_model=GuardrailSettings)
async def update_guardrail_settings(
    course_id: str, 
    request: UpdateGuardrailRequest, 
    professor_id: str = "prof1"
):
    """Update guardrail settings"""
    return professor_service.update_guardrail_settings(course_id, request, professor_id)

# ============================================================================
# ADAPTIVE LEARNING ENDPOINTS
# ============================================================================

@app.get("/api/adaptive/daily-quiz", response_model=DailyQuizResponse)
async def get_daily_quiz(student_id: str = "student1", count: int = 3):
    """
    Get personalized daily pop quiz (spaced repetition)
    Returns 3 items based on forgetting curve, weak topics, and new material
    """
    if not pop_quiz_service:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    items = pop_quiz_service.get_daily_quiz(student_id, num_items=count)
    
    # Get mastery summary
    mastery_summary = {}
    if student_id in spaced_rep_engine.student_mastery:
        for topic, mastery in spaced_rep_engine.student_mastery[student_id].items():
            mastery_summary[topic] = round(mastery.mastery_score, 2)
    
    return DailyQuizResponse(
        date=datetime.now().strftime("%Y-%m-%d"),
        items=[
            PopQuizItemResponse(
                question_id=item.question_id,
                topic=item.topic,
                subtopic=item.subtopic,
                question=item.question,
                options=item.options,
                difficulty=item.difficulty,
                source_citation=item.source_citation
            )
            for item in items
        ],
        mastery_summary=mastery_summary
    )

@app.post("/api/adaptive/submit-answer", response_model=SubmitAnswerResponse)
async def submit_answer(request: SubmitAnswerRequest):
    """
    Submit answer to a pop quiz item
    Updates spaced repetition schedule and mastery tracking
    """
    if not pop_quiz_service:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    # Find the quiz item
    quiz_item = None
    for topic_items in pop_quiz_service.question_bank.values():
        for item in topic_items:
            if item.question_id == request.question_id:
                quiz_item = item
                break
        if quiz_item:
            break
    
    if not quiz_item:
        raise HTTPException(status_code=404, detail="Question not found")
    
    result = pop_quiz_service.submit_answer(
        request.student_id,
        quiz_item,
        request.selected_index,
        request.response_time_seconds
    )
    
    return SubmitAnswerResponse(**result)

@app.get("/api/adaptive/concept-check")
async def get_concept_check(student_id: str, topic: str, num_items: int = 2):
    """
    Get quick concept check for a specific topic (used during struggle)
    Returns easiest items to gauge understanding
    """
    if not pop_quiz_service:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    items = pop_quiz_service.get_concept_check(student_id, topic, num_items)
    
    return {
        "topic": topic,
        "items": [
            PopQuizItemResponse(
                question_id=item.question_id,
                topic=item.topic,
                subtopic=item.subtopic,
                question=item.question,
                options=item.options,
                difficulty=item.difficulty,
                source_citation=item.source_citation
            )
            for item in items
        ]
    }

@app.get("/api/adaptive/mastery-status", response_model=MasteryStatusResponse)
async def get_mastery_status(student_id: str = "student1"):
    """Get student's mastery status across all topics"""
    if not spaced_rep_engine:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    topics_data = []
    weak_topics = []
    strong_topics = []
    
    if student_id in spaced_rep_engine.student_mastery:
        for topic, mastery in spaced_rep_engine.student_mastery[student_id].items():
            topic_data = {
                "topic": topic,
                "mastery_score": round(mastery.mastery_score, 2),
                "confidence": round(mastery.confidence, 2),
                "attempts": mastery.attempts,
                "correct": mastery.correct,
                "streak": mastery.streak
            }
            topics_data.append(topic_data)
            
            if mastery.mastery_score < 0.6:
                weak_topics.append(topic)
            elif mastery.mastery_score >= 0.8:
                strong_topics.append(topic)
    
    overall_progress = sum(t["mastery_score"] for t in topics_data) / len(topics_data) if topics_data else 0.0
    
    return MasteryStatusResponse(
        student_id=student_id,
        topics=topics_data,
        weak_topics=weak_topics,
        strong_topics=strong_topics,
        overall_progress=round(overall_progress, 2)
    )

@app.post("/api/adaptive/exam-runway", response_model=ExamRunwayResponse)
async def create_exam_runway(request: ExamRunwayRequest):
    """
    Generate 7-day exam preparation plan
    Includes daily targets, gap checks, and mock exam
    """
    if not exam_runway_service:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    exam_date = datetime.fromisoformat(request.exam_date)
    
    runway = exam_runway_service.generate_runway(
        request.student_id,
        exam_date,
        request.exam_type,
        request.hours_per_day,
        request.course_id
    )
    
    return ExamRunwayResponse(
        exam_type=runway.exam_type,
        exam_date=runway.exam_date.isoformat(),
        days_until_exam=runway.days_until_exam,
        daily_targets=[
            {
                "day_number": target.day_number,
                "date": target.date.strftime("%Y-%m-%d"),
                "focus_topics": target.focus_topics,
                "time_blocks": [
                    {
                        "day": task.day,
                        "focus": task.focus,
                        "duration_hours": task.duration_hours
                    }
                    for task in target.time_blocks
                ],
                "gap_check_items": target.gap_check_items,
                "intensity": target.intensity
            }
            for target in runway.daily_targets
        ],
        priority_topics=runway.priority_topics,
        total_hours_allocated=runway.total_hours_allocated
    )

@app.get("/api/adaptive/gap-check")
async def get_gap_check(student_id: str, exam_type: str, day_number: int):
    """Get gap check questions for a specific day in exam runway"""
    if not exam_runway_service:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    # This would need the runway stored somewhere, for now return concept check
    # In production, store runway in database or session
    return {"message": "Gap check endpoint - implementation needs runway persistence"}

@app.get("/api/adaptive/mock-exam", response_model=MockExamResponse)
async def get_mock_exam(student_id: str, exam_type: str):
    """Generate 20-minute mock exam for practice"""
    if not exam_runway_service:
        raise HTTPException(status_code=503, detail="Adaptive learning not initialized")
    
    questions = exam_runway_service.generate_mock_exam(student_id, exam_type)
    
    return MockExamResponse(
        exam_type=exam_type,
        num_questions=len(questions),
        time_limit_minutes=20,
        questions=[
            PopQuizItemResponse(
                question_id=q["question_id"],
                topic=q["topic"],
                subtopic=q.get("subtopic", ""),
                question=q["question"],
                options=q["options"],
                difficulty=q.get("difficulty", 0.5),
                source_citation=q.get("source", "Mock Exam")
            )
            for q in questions
        ]
    )

# Behavioral Tracking Endpoints

@app.post("/api/adaptive/behavior/start-session")
async def start_behavior_session(request: BehaviorSessionRequest):
    """Start tracking a behavioral session"""
    if not behavioral_tracker:
        raise HTTPException(status_code=503, detail="Behavioral tracking not initialized")
    
    session = behavioral_tracker.start_session(
        request.session_id,
        request.student_id,
        request.topic
    )
    
    return {
        "session_id": session.session_id,
        "started": True,
        "timestamp": session.start_time.isoformat()
    }

@app.post("/api/adaptive/behavior/log")
async def log_behavior_event(request: BehaviorLogRequest):
    """Log a behavioral event (hint request, question, error, etc.)"""
    if not behavioral_tracker:
        raise HTTPException(status_code=503, detail="Behavioral tracking not initialized")
    
    session_id = request.session_id
    event_type = request.event_type
    
    if event_type == "hint":
        behavioral_tracker.log_hint_request(session_id)
    elif event_type == "question":
        question_text = request.data.get("question", "")
        behavioral_tracker.log_question(session_id, question_text)
    elif event_type == "error":
        error_type = request.data.get("error_type", "unknown")
        behavioral_tracker.log_error(session_id, error_type)
    elif event_type == "copy_paste":
        behavioral_tracker.log_copy_paste(session_id)
    
    # Update time on task
    behavioral_tracker.update_time_on_task(session_id)
    
    return {"logged": True, "event_type": event_type}

@app.get("/api/adaptive/behavior/check-intervention", response_model=InterventionCheckResponse)
async def check_intervention(session_id: str):
    """Check if intervention should be offered based on behavioral signals"""
    if not behavioral_tracker:
        raise HTTPException(status_code=503, detail="Behavioral tracking not initialized")
    
    intervention = behavioral_tracker.should_offer_intervention(session_id)
    
    return InterventionCheckResponse(**intervention)

@app.post("/api/adaptive/behavior/intervention-response")
async def record_intervention_response(session_id: str, accepted: bool):
    """Record whether student accepted the intervention"""
    if not behavioral_tracker:
        raise HTTPException(status_code=503, detail="Behavioral tracking not initialized")
    
    behavioral_tracker.record_intervention_response(session_id, accepted)
    
    return {"recorded": True, "accepted": accepted}

@app.post("/api/adaptive/behavior/end-session")
async def end_behavior_session(session_id: str):
    """End a behavioral tracking session"""
    if not behavioral_tracker:
        raise HTTPException(status_code=503, detail="Behavioral tracking not initialized")
    
    summary = behavioral_tracker.end_session(session_id)
    
    return summary

# Notification/Reminder Endpoints

@app.get("/api/adaptive/notifications")
async def get_notifications(student_id: str = "student1"):
    """Get pending and upcoming notifications for a student"""
    if not reminder_service:
        raise HTTPException(status_code=503, detail="Reminder service not initialized")
    
    pending = reminder_service.get_pending_reminders(student_id)
    upcoming = reminder_service.get_upcoming_reminders(student_id, hours_ahead=24)
    
    # Convert to notification format
    notifications = []
    for reminder in pending + upcoming:
        notifications.append({
            "id": reminder.reminder_id,
            "type": reminder.reminder_type,
            "message": reminder.message,
            "timestamp": reminder.scheduled_time.isoformat(),
            "action_url": reminder.data.get("action_url"),
            "data": reminder.data,
            "read": reminder.sent
        })
    
    unread_count = len([n for n in notifications if not n["read"]])
    
    return {
        "notifications": notifications,
        "unread_count": unread_count
    }

@app.post("/api/adaptive/notifications/{notification_id}/read")
async def mark_notification_read(notification_id: str, student_id: str = "student1"):
    """Mark a notification as read"""
    if not reminder_service:
        raise HTTPException(status_code=503, detail="Reminder service not initialized")
    
    reminder_service.mark_as_sent(notification_id, student_id)
    
    return {"success": True}

@app.post("/api/adaptive/reminders/schedule-daily-quiz")
async def schedule_daily_quiz(student_id: str = "student1"):
    """Schedule a daily quiz reminder"""
    if not reminder_service:
        raise HTTPException(status_code=503, detail="Reminder service not initialized")
    
    reminder = reminder_service.schedule_daily_quiz_reminder(student_id)
    
    return {
        "reminder_id": reminder.reminder_id,
        "scheduled_time": reminder.scheduled_time.isoformat(),
        "message": reminder.message
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
