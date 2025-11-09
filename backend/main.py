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
    GuardrailSettings, UpdateGuardrailRequest
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

@app.on_event("startup")
async def startup_event():
    """Initialize the multi-agent system on startup"""
    global retriever, orchestrator, professor_service
    
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
    
    assignment_helper = AssignmentHelperAgent()
    assignment_helper.register_tool(retrieval_tool)
    assignment_helper.register_tool(citation_tool)
    assignment_helper.register_tool(analytics_tool)
    assignment_helper.register_tool(guardrail_tool)
    orchestrator.register_agent(assignment_helper)
    
    study_plan_agent = StudyPlanAgent()
    orchestrator.register_agent(study_plan_agent)
    
    print("✅ Multi-Agent System Ready!")
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
