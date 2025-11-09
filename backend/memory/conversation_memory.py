"""
Conversation Memory
Stores conversation history and context
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class ConversationTurn(BaseModel):
    """Single turn in a conversation"""
    turn_id: str
    timestamp: datetime
    speaker: str  # "user" or agent_id
    message: str
    metadata: Dict[str, Any] = {}

class ConversationMemory:
    """
    Manages conversation history and context for a session
    """
    
    def __init__(self, conversation_id: str, student_id: str):
        self.conversation_id = conversation_id
        self.student_id = student_id
        self.turns: List[ConversationTurn] = []
        self.context: Dict[str, Any] = {}
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        
    def add_turn(self, speaker: str, message: str, metadata: Dict[str, Any] = None):
        """Add a conversation turn"""
        turn = ConversationTurn(
            turn_id=f"{self.conversation_id}_{len(self.turns)}",
            timestamp=datetime.now(),
            speaker=speaker,
            message=message,
            metadata=metadata or {}
        )
        self.turns.append(turn)
        self.updated_at = datetime.now()
        
    def get_recent_turns(self, n: int = 5) -> List[ConversationTurn]:
        """Get the n most recent turns"""
        return self.turns[-n:]
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get a context value"""
        return self.context.get(key, default)
    
    def set_context(self, key: str, value: Any):
        """Set a context value"""
        self.context[key] = value
        self.updated_at = datetime.now()
    
    def get_full_history(self) -> List[Dict[str, Any]]:
        """Get full conversation history as dict"""
        return [
            {
                "speaker": turn.speaker,
                "message": turn.message,
                "timestamp": turn.timestamp.isoformat(),
                "metadata": turn.metadata
            }
            for turn in self.turns
        ]
    
    def clear(self):
        """Clear conversation history"""
        self.turns = []
        self.context = {}
        self.updated_at = datetime.now()
