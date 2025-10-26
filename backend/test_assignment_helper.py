"""
Test script for Assignment Helper functionality
"""
import sys
from pathlib import Path

# Add the backend directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from assignment_helper import AssignmentHelper
from models import AssignmentHelpRequest
from document_store import DocumentStore, DocumentChunk

def test_assignment_helper():
    """Test the assignment helper with sample questions"""
    
    helper = AssignmentHelper()
    
    # Sample assignment chunk
    sample_chunk = DocumentChunk(
        text="""## PROBLEM 2: MARIO
Implement a program that prints a half-pyramid of a specified height using hashes (#).

Requirements:
- Prompt user for height (between 1 and 8, inclusive)
- If invalid input, re-prompt
- Print right-aligned pyramid""",
        source="cs50_assignment1.txt",
        section="Problem 2: Mario",
        metadata={}
    )
    
    test_cases = [
        {
            "request": AssignmentHelpRequest(
                question="How do I start the Mario problem?",
                problem_number="Problem 2"
            ),
            "description": "Getting started question"
        },
        {
            "request": AssignmentHelpRequest(
                question="My code has an error and I don't know why",
                problem_number="Problem 2",
                context="I tried to print the pyramid but it's not working"
            ),
            "description": "Debugging question"
        },
        {
            "request": AssignmentHelpRequest(
                question="What algorithm should I use to create the pyramid?",
                problem_number="Problem 2"
            ),
            "description": "Algorithm design question"
        },
        {
            "request": AssignmentHelpRequest(
                question="How do I write a loop in C?",
                problem_number="Problem 2"
            ),
            "description": "Implementation question"
        }
    ]
    
    print("🧪 Testing Assignment Helper\n")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n\n📋 TEST CASE {i}: {test_case['description']}")
        print(f"Question: {test_case['request'].question}")
        print("-" * 80)
        
        # Simulate retrieved chunks
        retrieved_chunks = [(sample_chunk, 0.85)]
        
        response = helper.help_with_assignment(test_case['request'], retrieved_chunks)
        
        print(f"\n💡 GUIDANCE:\n{response.guidance}")
        print(f"\n📚 KEY CONCEPTS: {', '.join(response.concepts)}")
        print(f"\n📖 RESOURCES: {', '.join(response.resources)}")
        print(f"\n➡️ NEXT STEPS:")
        for step in response.next_steps:
            print(f"   - {step}")
        print(f"\n📎 CITATIONS: {len(response.citations)} relevant sources")
        
        print("\n" + "=" * 80)
    
    print("\n✅ All tests completed!")
    print("\nNote: The helper provides guidance without giving direct answers,")
    print("encouraging students to think through problems and learn actively.")

if __name__ == "__main__":
    test_assignment_helper()
