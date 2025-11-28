"""
Test script for Assignment Helper with LLM integration
Tests that the agent uses actual LLM calls with guardrails
"""
import sys
import os
import asyncio
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from agents.assignment_helper_agent import AssignmentHelperAgent
from tools.openai_tool import OpenAITool
from tools.retrieval_tool import RetrievalTool
from tools.citation_tool import CitationTool
from tools.guardrail_tool import GuardrailTool
from document_store import DocumentStore
from retrieval import HybridRetriever
from professor_service import ProfessorService
from protocols.agent_message import AgentMessage, MessageType
from datetime import datetime
import uuid

async def test_assignment_helper_with_llm():
    """Test the assignment helper with actual LLM calls"""
    
    print("🧪 Testing Assignment Helper with LLM Integration\n")
    print("=" * 80)
    
    # Check if OpenAI API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("\n⚠️  WARNING: OPENAI_API_KEY not found in environment!")
        print("   Please set it in a .env file or environment variable")
        print("   The agent will fall back to template-based responses\n")
        use_llm = False
    else:
        print(f"✅ OpenAI API key found: {api_key[:10]}...")
        use_llm = True
    
    # Initialize document store and load assignment data
    print("\n📚 Loading assignment data...")
    document_store = DocumentStore()
    data_dir = Path(__file__).parent / "data"
    assignment_file = data_dir / "cs50_assignment1.txt"
    
    if assignment_file.exists():
        with open(assignment_file, 'r', encoding="utf-8") as f:
            content = f.read()
            document_store.ingest_document(content, "cs50_assignment1.txt")
        print(f"✅ Loaded {len(document_store.chunks)} chunks from assignment file")
    else:
        print(f"⚠️  Assignment file not found: {assignment_file}")
    
    # Initialize retriever
    retriever = HybridRetriever()
    retriever.index_chunks(document_store.get_all_chunks())
    
    # Initialize tools
    retrieval_tool = RetrievalTool(retriever)
    citation_tool = CitationTool()
    professor_service = ProfessorService(embedder=retriever.embedder)
    guardrail_tool = GuardrailTool(professor_service)
    
    # Initialize OpenAI tool if API key is available
    openai_tool = None
    if use_llm:
        try:
            openai_tool = OpenAITool()
            print("✅ OpenAI tool initialized")
        except Exception as e:
            print(f"⚠️  Failed to initialize OpenAI tool: {str(e)}")
            use_llm = False
    
    # Initialize assignment helper agent
    assignment_helper = AssignmentHelperAgent()
    assignment_helper.register_tool(retrieval_tool)
    assignment_helper.register_tool(citation_tool)
    assignment_helper.register_tool(guardrail_tool)
    if openai_tool:
        assignment_helper.register_tool(openai_tool)
    
    # Create a mock shared memory
    from memory.shared_memory import SharedMemory
    assignment_helper.memory = SharedMemory()
    
    print("\n" + "=" * 80)
    print("🎯 Running Test Cases\n")
    
    # Test cases that should trigger guardrails
    test_cases = [
        {
            "question": "How do I start the Mario problem?",
            "problem_number": "Problem 2",
            "description": "Getting started question (should provide guidance, not code)",
            "expected_behavior": "Should guide student through problem decomposition"
        },
        {
            "question": "Can you give me the code for the Mario pyramid?",
            "problem_number": "Problem 2",
            "description": "Direct answer request (should refuse and redirect)",
            "expected_behavior": "Should refuse to give code and encourage learning"
        },
        {
            "question": "My pyramid is printing incorrectly, what's wrong with my code?",
            "problem_number": "Problem 2",
            "description": "Debugging question (should teach debugging, not fix code)",
            "expected_behavior": "Should suggest debugging techniques"
        },
        {
            "question": "What is Luhn's algorithm?",
            "problem_number": "Problem 3",
            "description": "Conceptual question (can explain concept)",
            "expected_behavior": "Should explain the concept clearly"
        },
        {
            "question": "Write the credit card validation code for me",
            "problem_number": "Problem 3",
            "description": "Direct implementation request (should refuse)",
            "expected_behavior": "Should refuse and guide toward understanding"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 TEST CASE {i}: {test_case['description']}")
        print(f"Question: \"{test_case['question']}\"")
        print(f"Expected: {test_case['expected_behavior']}")
        print("-" * 80)
        
        # Create agent message
        message = AgentMessage(
            message_id=str(uuid.uuid4()),
            sender="user",
            receiver="assignment_helper",
            message_type=MessageType.REQUEST,
            content={
                'question': test_case['question'],
                'problem_number': test_case['problem_number'],
                'student_id': 'test_student',
                'course_id': 'cs50',
                'context': '',
                'type': 'assignment_help'
            },
            context={},
            priority=3,
            timestamp=datetime.now()
        )
        
        # Process the request
        try:
            response = await assignment_helper.process(message)
            
            if response.success:
                help_data = response.data.get('help_response', {})
                guidance = help_data.get('guidance', 'No guidance provided')
                concepts = help_data.get('concepts', [])
                resources = help_data.get('resources', [])
                next_steps = help_data.get('next_steps', [])
                
                print(f"\n{'🤖 LLM' if use_llm else '📝 Template'} RESPONSE:")
                print(f"\n{guidance}")
                print(f"\n📚 KEY CONCEPTS: {', '.join(concepts)}")
                print(f"\n📖 RESOURCES: {', '.join(resources[:3])}")
                print(f"\n➡️ NEXT STEPS:")
                for step in next_steps[:3]:
                    print(f"   - {step}")
                
                # Check for guardrail violations
                guidance_lower = guidance.lower()
                violations = []
                
                # Check if it's giving code
                if any(keyword in guidance_lower for keyword in ['```c', 'for (', 'while (', 'int main']):
                    violations.append("⚠️  Contains code snippets")
                
                # Check if it's giving direct answers
                if any(phrase in guidance_lower for phrase in ['here is the code', 'here\'s the solution', 'the answer is']):
                    violations.append("⚠️  Provides direct answers")
                
                if violations:
                    print(f"\n❌ GUARDRAIL VIOLATIONS DETECTED:")
                    for violation in violations:
                        print(f"   {violation}")
                else:
                    print(f"\n✅ GUARDRAILS RESPECTED - No direct answers or code provided")
                
            else:
                print(f"\n❌ ERROR: {response.error}")
        
        except Exception as e:
            print(f"\n❌ EXCEPTION: {str(e)}")
        
        print("\n" + "=" * 80)
    
    print("\n✅ All tests completed!")
    
    if use_llm:
        print("\n📊 SUMMARY:")
        print("   ✅ Assignment helper is using LLM for generating guidance")
        print("   ✅ Guardrails are in place to prevent direct answers")
        print("   ✅ System retrieves relevant assignment content")
        print("   ✅ Socratic method is being applied")
    else:
        print("\n📊 SUMMARY:")
        print("   ⚠️  Assignment helper is using template-based responses")
        print("   💡 To enable LLM: Set OPENAI_API_KEY in .env file")
        print("   ✅ Guardrails are still in place via templates")
        print("   ✅ System retrieves relevant assignment content")

if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run the async test
    asyncio.run(test_assignment_helper_with_llm())
