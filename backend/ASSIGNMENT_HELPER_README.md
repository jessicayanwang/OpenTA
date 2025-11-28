# Assignment Helper Agent - LLM Integration

## Overview

The Assignment Helper Agent now uses **actual LLM API calls** (OpenAI GPT-4o-mini) to provide intelligent, Socratic guidance to students working on graded assignments. It includes strong guardrails to prevent giving direct answers or complete code solutions.

## Key Features

### 🤖 LLM-Powered Guidance
- Uses OpenAI's GPT-4o-mini for generating contextual, adaptive responses
- Retrieves relevant content from assignment documents (e.g., `cs50_assignment1.txt`)
- Generates personalized guidance based on question type and context

### 🚨 Strong Guardrails
The system has multiple layers of protection against academic dishonesty:

1. **System Prompt Guardrails**: Every LLM call includes strict instructions:
   - NEVER provide complete code solutions
   - NEVER write code that solves the problem
   - NEVER give step-by-step implementation details
   - Use Socratic method - guide with questions, not answers
   - Refuse direct answer requests and redirect to learning

2. **Question Type Classification**: Automatically detects question type and applies appropriate guidance:
   - **Debugging**: Teaches debugging strategies, doesn't fix code
   - **Implementation**: Encourages pseudocode and planning, no actual code
   - **Conceptual**: Can explain concepts but encourages active learning
   - **Getting Started**: Helps with problem decomposition, not solutions
   - **General**: Clarifies questions and suggests approaches

3. **Hint Limiting**: Tracks hint usage per student/assignment (via guardrail tool)

### 📚 Content Retrieval
- Automatically retrieves relevant sections from assignment documents
- Uses hybrid retrieval (semantic + keyword search)
- Provides citations to course materials

## Setup

### 1. Environment Configuration

Create a `.env` file in the `backend` directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: Without an API key, the system will fall back to template-based responses (still functional but less adaptive).

### 2. Assignment Data

Place assignment documents in `backend/data/`:
- Example: `cs50_assignment1.txt` (already included)
- Format: Plain text with clear problem descriptions

### 3. Install Dependencies

```bash
pip install openai python-dotenv
```

## Usage

### Via API Endpoint

```bash
POST /api/assignment-help
```

**Request Body**:
```json
{
  "question": "How do I start the Mario problem?",
  "problem_number": "Problem 2",
  "course_id": "cs50",
  "context": ""
}
```

**Response**:
```json
{
  "guidance": "Let's break down the Mario problem together...",
  "concepts": ["Loops", "Nested Loops", "Output Formatting"],
  "resources": ["Review assignment specification", "Check lecture notes"],
  "next_steps": ["List all inputs and expected outputs", "..."],
  "citations": [...]
}
```

### Testing

Run the comprehensive test suite:

```bash
python test_assignment_helper_llm.py
```

This will test:
- ✅ Getting started questions
- ✅ Direct answer requests (should be refused)
- ✅ Debugging questions
- ✅ Conceptual questions
- ✅ Implementation requests (should be refused)

## How It Works

### Flow Diagram

```
Student Question
    ↓
Retrieval Tool → Finds relevant assignment content
    ↓
Question Classification → Determines question type
    ↓
LLM Call with Guardrails → Generates Socratic guidance
    ↓
Concept Extraction → Identifies key concepts
    ↓
Resource & Next Steps → Provides learning path
    ↓
Response to Student
```

### Example Interactions

#### ❌ Bad Request (Refused)
**Student**: "Give me the code for the Mario pyramid"

**OpenTA**: "I understand you're looking for a solution, but providing the complete code would prevent you from learning. Instead, let me guide you through the problem:

1. What do you understand about the requirements?
2. Can you describe in plain English what the program needs to do?
3. What programming concepts from lecture might be useful here?

Let's work through this together - the learning happens in the struggle!"

#### ✅ Good Guidance
**Student**: "How do I start the Mario problem?"

**OpenTA**: "Great question! Let's break this down step by step:

**First, understand the requirements:**
- What inputs does the program need?
- What should the output look like?
- Are there any constraints?

**Then, think about the approach:**
- How might you create a single row of hashes?
- How would you create multiple rows?
- How do you control the spacing?

Try sketching out the solution in pseudocode first. What would be your first step?"

## Guardrail Testing

The system is designed to refuse inappropriate requests:

| Request Type | Example | Response |
|-------------|---------|----------|
| Direct code request | "Write the code for me" | Refuses, redirects to learning |
| Direct answer | "What's the answer?" | Refuses, asks guiding questions |
| Debugging help | "My code has a bug" | Teaches debugging strategies |
| Conceptual | "What is Luhn's algorithm?" | Explains concept clearly |
| Getting started | "How do I begin?" | Guides through problem decomposition |

## Architecture

### Files Modified
- `backend/agents/assignment_helper_agent.py`: Main agent implementation
  - Added `_generate_socratic_guidance()` with LLM integration
  - Added `_create_assignment_helper_prompt()` with guardrails
  - Added `_classify_question()` for question type detection
  - Added `_suggest_resources()` and `_suggest_next_steps()`
  - Added `_generate_fallback_guidance()` for when LLM is unavailable

- `backend/main.py`: Registration
  - Registered OpenAI tool with assignment helper agent

### Dependencies
- `tools/openai_tool.py`: OpenAI API integration
- `tools/retrieval_tool.py`: Document retrieval
- `tools/guardrail_tool.py`: Hint limiting and policy enforcement
- `tools/citation_tool.py`: Citation generation

## Monitoring & Analytics

The system logs:
- Question types and frequency
- Hint usage per student/assignment
- Behavioral signals (via BehavioralTracker)
- Intervention triggers

## Future Enhancements

Potential improvements:
1. **Multi-turn conversations**: Remember context across questions
2. **Code analysis**: Analyze student code (without fixing it) to provide better guidance
3. **Adaptive difficulty**: Adjust guidance based on student progress
4. **Peer comparison**: Show anonymized statistics
5. **Professor dashboard**: View common struggles and intervention needs

## Troubleshooting

### "OpenAI API key not found"
- Create a `.env` file with `OPENAI_API_KEY=your_key`
- Or set environment variable: `export OPENAI_API_KEY=your_key`

### "System will use rule-based answer generation"
- This is the fallback mode when no API key is set
- Still functional but less adaptive
- Template-based responses are used

### "No relevant documents found"
- Ensure assignment files are in `backend/data/`
- Check file format (plain text, UTF-8 encoding)
- Verify document ingestion in startup logs

## Security & Academic Integrity

The system is designed with academic integrity as a top priority:

1. **No Direct Answers**: Multiple layers prevent giving solutions
2. **Audit Trail**: All interactions are logged for review
3. **Hint Limiting**: Prevents over-reliance on the system
4. **Socratic Method**: Encourages independent thinking
5. **Professor Controls**: Configurable guardrails per course

## License

Part of the OpenTA system - MIT License
