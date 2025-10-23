"""
OpenTA Backend - FastAPI Application
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

from models import ChatRequest, ChatResponse
from document_store import DocumentStore
from retrieval import HybridRetriever
from qa_agent import QAAgent

app = FastAPI(title="OpenTA API", version="0.1.0")

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
qa_agent = None

@app.on_event("startup")
async def startup_event():
    """Initialize the system on startup"""
    global retriever, qa_agent
    
    print("🚀 Starting OpenTA...")
    
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
    
    # Initialize QA agent (no API key needed)
    qa_agent = QAAgent()
    
    print("✅ OpenTA is ready!")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "OpenTA API",
        "version": "0.1.0",
        "status": "running"
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "chunks_indexed": len(document_store.chunks) if document_store else 0
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - answers questions with grounded responses
    """
    if not retriever or not qa_agent:
        raise HTTPException(status_code=503, detail="System not initialized")
    
    print(f"\n❓ Question: {request.question}")
    
    # Retrieve relevant chunks
    retrieved_chunks = retriever.retrieve(request.question, top_k=3)
    
    if not retrieved_chunks:
        return ChatResponse(
            answer="I couldn't find relevant information in the course materials to answer your question.",
            citations=[],
            confidence=0.0
        )
    
    print(f"📖 Retrieved {len(retrieved_chunks)} relevant chunks")
    
    # Generate answer with citations
    response = qa_agent.generate_answer(request.question, retrieved_chunks)
    
    print(f"✅ Answer generated (confidence: {response.confidence:.2f})")
    
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
