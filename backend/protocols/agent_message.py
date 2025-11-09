"""
Agent Message Protocol
Defines how agents communicate with each other
"""
from enum import Enum
from typing import Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

class MessageType(str, Enum):
    """Types of messages agents can send"""
    REQUEST = "request"           # Agent needs help from another agent
    RESPONSE = "response"         # Reply to a request
    SIGNAL = "signal"             # Broadcast information
    ESCALATION = "escalation"     # Needs human intervention
    TOOL_CALL = "tool_call"       # Request to use a tool
    TOOL_RESULT = "tool_result"   # Result from tool execution

class AgentMessage(BaseModel):
    """
    Standard message format for agent communication
    """
    message_id: str
    sender: str                    # Agent ID that sent the message
    receiver: str                  # Target agent or "orchestrator" or "broadcast"
    message_type: MessageType
    content: Dict[str, Any]        # Message payload
    context: Dict[str, Any] = {}   # Shared context (conversation history, student info, etc.)
    priority: int = 3              # 1 (highest) to 5 (lowest)
    timestamp: datetime
    parent_message_id: Optional[str] = None  # For threading conversations
    metadata: Dict[str, Any] = {}
    
    class Config:
        use_enum_values = True

class AgentResponse(BaseModel):
    """
    Standard response format from agents
    """
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    agent_id: str
    confidence: float = 1.0
    reasoning: Optional[str] = None  # Explanation of agent's decision
    next_actions: list = []          # Suggested next steps
