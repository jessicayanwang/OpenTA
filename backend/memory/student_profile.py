"""
Student Profile
Tracks student learning patterns and progress
"""
from typing import Dict, Any, List
from datetime import datetime

class StudentProfile:
    """
    Stores student-specific information and learning analytics
    """
    
    def __init__(self, student_id: str):
        self.student_id = student_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
        # Learning analytics
        self.questions_asked = 0
        self.topics_explored: List[str] = []
        self.confusion_signals: List[Dict[str, Any]] = []
        self.hint_usage: Dict[str, int] = {}  # assignment_id -> hint_count
        
        # Preferences and patterns
        self.learning_style: str = "unknown"
        self.preferred_explanation_depth: str = "medium"
        
        # Progress tracking
        self.completed_assignments: List[str] = []
        self.study_plan_progress: Dict[str, Any] = {}
        
    def log_question(self, question: str, topic: str = None):
        """Log a question asked by the student"""
        self.questions_asked += 1
        if topic and topic not in self.topics_explored:
            self.topics_explored.append(topic)
        self.updated_at = datetime.now()
    
    def log_confusion(self, artifact: str, question: str, signal_type: str):
        """Log a confusion signal"""
        self.confusion_signals.append({
            "artifact": artifact,
            "question": question,
            "signal_type": signal_type,
            "timestamp": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def increment_hint_usage(self, assignment_id: str):
        """Increment hint usage for an assignment"""
        if assignment_id not in self.hint_usage:
            self.hint_usage[assignment_id] = 0
        self.hint_usage[assignment_id] += 1
        self.updated_at = datetime.now()
    
    def get_hint_count(self, assignment_id: str) -> int:
        """Get number of hints used for an assignment"""
        return self.hint_usage.get(assignment_id, 0)
    
    def is_struggling(self) -> bool:
        """Determine if student is struggling based on confusion signals"""
        recent_confusions = [
            c for c in self.confusion_signals
            if (datetime.now() - datetime.fromisoformat(
                c["timestamp"].replace('Z', '+00:00') if 'Z' in c["timestamp"] else c["timestamp"]
            )).seconds < 3600
        ]
        return len(recent_confusions) >= 3
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary"""
        return {
            "student_id": self.student_id,
            "questions_asked": self.questions_asked,
            "topics_explored": self.topics_explored,
            "confusion_count": len(self.confusion_signals),
            "learning_style": self.learning_style,
            "hint_usage": self.hint_usage
        }
