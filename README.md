# OpenTA - AI Teaching Assistant MVP

An agentic teaching assistant that provides grounded, citation-backed answers to course questions.

## 🎯 MVP Features

This MVP demonstrates **one complete end-to-end task**: answering course logistics and content questions with citations from ingested course materials.

### What Works
- ✅ Document ingestion and chunking (syllabus, assignments)
- ✅ Hybrid retrieval (BM25 + semantic search)
- ✅ Grounded Q&A with source citations
- ✅ Clean chat interface with confidence scores
- ✅ Sample CS50 course data

### Example Questions
- "When is Problem Set 1 due?"
- "What is the late policy?"
- "What are the office hours?"
- "What does Problem 2 in Assignment 1 ask?"

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 18+
- OpenAI API key (optional - has fallback mode)

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file (optional):
```bash
cp .env.example .env
# Add your OpenAI API key to .env
```

4. Run the backend:
```bash
python main.py
```

Backend will run on `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

Frontend will run on `http://localhost:3000`

## 📁 Project Structure

```
OpenTA/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Pydantic models
│   ├── document_store.py    # Document ingestion & chunking
│   ├── retrieval.py         # Hybrid retrieval system
│   ├── qa_agent.py          # Q&A agent with citations
│   ├── data/                # Course materials
│   │   ├── cs50_syllabus.txt
│   │   └── cs50_assignment1.txt
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx         # Main chat interface
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   └── tailwind.config.js
└── README.md
```

## 🔧 Tech Stack

### Backend
- **FastAPI**: REST API framework
- **BM25**: Keyword-based retrieval
- **OpenAI API**: LLM for answer generation (with fallback)
- **NumPy/scikit-learn**: Embeddings and similarity

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling

## 🎓 How It Works

1. **Document Ingestion**: Course materials are chunked by sections with metadata
2. **Hybrid Retrieval**: User questions trigger both BM25 and semantic search
3. **Answer Generation**: Retrieved chunks are sent to LLM with prompt engineering
4. **Citation Display**: Sources are shown with relevance scores

## 📊 Current Limitations (MVP)

- Uses simulated embeddings (production should use OpenAI embeddings API)
- Limited to 2 sample documents
- No guardrails for graded content yet
- No study plan generator yet
- No admin interface for uploading documents

## 🔜 Next Steps (Post-MVP)

- Real OpenAI embeddings integration
- Graded-item detection and hint-only mode
- Study plan generator
- Admin upload interface
- Analytics dashboard
- Intent classification
- Code debugging helper

## 🧪 Testing

Try these questions to test the system:

1. **Logistics**: "When is Problem Set 1 due?"
2. **Policy**: "What is the late policy?"
3. **Content**: "What does the Mario problem ask for?"
4. **Support**: "What are the office hours?"

## 📝 Notes

- The system works in fallback mode without an OpenAI API key
- Sample data is from CS50 (for demonstration purposes)
- Citations show exact source documents and sections
- Confidence scores indicate answer reliability

## 🤝 Contributing

This is an MVP. Future enhancements welcome!
