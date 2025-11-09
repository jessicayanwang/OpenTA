"""
Shared Memory System
Central memory accessible by all agents
"""
from typing import Dict, Optional
from .conversation_memory import ConversationMemory
from .student_profile import StudentProfile

class SharedMemory:
    """
    Central memory system that all agents can access
    Manages conversations, student profiles, and course knowledge
    """
    
    def __init__(self):
        self.conversations: Dict[str, ConversationMemory] = {}
        self.student_profiles: Dict[str, StudentProfile] = {}
        self.course_knowledge: Dict[str, any] = {}
        
    def get_or_create_conversation(self, conversation_id: str, student_id: str) -> ConversationMemory:
        """Get existing conversation or create new one"""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationMemory(conversation_id, student_id)
        return self.conversations[conversation_id]
    
    def get_conversation(self, conversation_id: str) -> Optional[ConversationMemory]:
        """Get a conversation by ID"""
        return self.conversations.get(conversation_id)
    
    def get_or_create_student_profile(self, student_id: str) -> StudentProfile:
        """Get existing student profile or create new one"""
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = StudentProfile(student_id)
        return self.student_profiles[student_id]
    
    def get_student_profile(self, student_id: str) -> Optional[StudentProfile]:
        """Get a student profile by ID"""
        return self.student_profiles.get(student_id)
    
    def store_knowledge(self, key: str, value: any):
        """Store course knowledge"""
        self.course_knowledge[key] = value
    
    def get_knowledge(self, key: str, default: any = None) -> any:
        """Retrieve course knowledge"""
        return self.course_knowledge.get(key, default)
    
    def clear_conversation(self, conversation_id: str):
        """Clear a specific conversation"""
        if conversation_id in self.conversations:
            del self.conversations[conversation_id]
    
    def get_stats(self) -> Dict[str, int]:
        """Get memory statistics"""
        return {
            "total_conversations": len(self.conversations),
            "total_students": len(self.student_profiles),
            "knowledge_items": len(self.course_knowledge)
        }
