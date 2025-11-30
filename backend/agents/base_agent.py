"""
Base Agent Class
All agents inherit from this class
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from enum import Enum
import uuid
from datetime import datetime

from protocols.agent_message import AgentMessage, AgentResponse, MessageType

class AgentCapability(str, Enum):
    """Capabilities that agents can have"""
    # Student-side capabilities
    ANSWER_QUESTIONS = "answer_questions"
    PROVIDE_HINTS = "provide_hints"
    GENERATE_STUDY_PLANS = "generate_study_plans"
    ANALYZE_CONFUSION = "analyze_confusion"
    VALIDATE_CITATIONS = "validate_citations"
    MANAGE_COURSE = "manage_course"
    RETRIEVE_DOCUMENTS = "retrieve_documents"
    
    # Professor-side capabilities
    CLUSTER_QUESTIONS = "cluster_questions"
    MANAGE_CANONICAL_ANSWERS = "manage_canonical_answers"
    MANAGE_UNRESOLVED_QUEUE = "manage_unresolved_queue"
    VIEW_DASHBOARD = "view_dashboard"
    ANALYZE_STUDENTS = "analyze_students"
    MANAGE_GUARDRAILS = "manage_guardrails"
    VIEW_CONFUSION_HEATMAP = "view_confusion_heatmap"
    IDENTIFY_CONTENT_GAPS = "identify_content_gaps"

class BaseAgent(ABC):
    """
    Abstract base class for all agents in the system
    """
    
    def __init__(self, agent_id: str, name: str, capabilities: List[AgentCapability]):
        self.agent_id = agent_id
        self.name = name
        self.capabilities = capabilities
        self.tools = []
        self.memory = None  # Will be set by orchestrator
        
    @abstractmethod
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process an incoming message and return a response
        Must be implemented by each agent
        """
        pass
    
    def can_handle(self, task_type: str) -> bool:
        """
        Check if this agent can handle a specific task type
        """
        return task_type in [cap.value for cap in self.capabilities]
    
    def register_tool(self, tool):
        """Register a tool that this agent can use"""
        self.tools.append(tool)
        
    def get_tool(self, tool_name: str):
        """Get a registered tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None
    
    def create_message(
        self,
        receiver: str,
        message_type: MessageType,
        content: Dict[str, Any],
        context: Dict[str, Any] = None,
        priority: int = 3
    ) -> AgentMessage:
        """Helper to create a message"""
        return AgentMessage(
            message_id=str(uuid.uuid4()),
            sender=self.agent_id,
            receiver=receiver,
            message_type=message_type,
            content=content,
            context=context or {},
            priority=priority,
            timestamp=datetime.now()
        )
    
    def create_response(
        self,
        success: bool,
        data: Dict[str, Any],
        confidence: float = 1.0,
        error: Optional[str] = None,
        reasoning: Optional[str] = None
    ) -> AgentResponse:
        """Helper to create a response"""
        return AgentResponse(
            success=success,
            data=data,
            error=error,
            agent_id=self.agent_id,
            confidence=confidence,
            reasoning=reasoning
        )
    
    async def use_tool(self, tool_name: str, params: Dict[str, Any]) -> Any:
        """Use a registered tool"""
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        return await tool.execute(params)
    
    def log(self, message: str, level: str = "INFO"):
        """Log agent activity"""
        print(f"[{level}] {self.agent_id}: {message}")
