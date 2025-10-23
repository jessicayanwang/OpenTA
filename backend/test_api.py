"""
Simple test script to verify the API works
Run this after starting the backend with: python main.py
"""
import requests
import json

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{API_URL}/api/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}\n")

def test_chat(question):
    """Test chat endpoint"""
    print(f"❓ Question: {question}")
    response = requests.post(
        f"{API_URL}/api/chat",
        json={
            "question": question,
            "course_id": "cs50"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Answer: {data['answer'][:200]}...")
        print(f"📊 Confidence: {data['confidence']:.2f}")
        print(f"📚 Citations: {len(data['citations'])} sources")
        
        for i, citation in enumerate(data['citations'][:2], 1):
            print(f"\n  Source {i}: {citation['source']} - {citation['section']}")
            print(f"  Relevance: {citation['relevance_score']:.2f}")
    else:
        print(f"❌ Error: {response.status_code}")
        print(response.text)
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    print("🚀 OpenTA API Test\n")
    print("="*80 + "\n")
    
    # Test health
    test_health()
    
    # Test various questions
    questions = [
        "When is Problem Set 1 due?",
        "What is the late policy?",
        "What are the office hours?",
        "What does the Mario problem ask for?"
    ]
    
    for question in questions:
        test_chat(question)
    
    print("✅ All tests completed!")
