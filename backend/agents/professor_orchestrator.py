"""
Professor Orchestrator Agent
Routes requests to appropriate professor-side agents and coordinates workflows
"""
from typing import Dict, Any, Optional

from .base_agent import BaseAgent
from protocols.agent_message import AgentMessage, AgentResponse, MessageType
from memory.shared_memory import SharedMemory


class ProfessorOrchestrator(BaseAgent):
    """
    Orchestrator for professor-side agents
    Routes requests to clustering, canonical answer, unresolved queue, 
    dashboard, and guardrail settings agents
    """
    
    def __init__(self, shared_memory: SharedMemory):
        super().__init__(
            agent_id="professor_orchestrator",
            name="Professor Orchestrator",
            capabilities=[]  # Orchestrator doesn't have specific capabilities
        )
        self.shared_memory = shared_memory
        self.agents: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register a professor-side agent"""
        self.agents[agent.agent_id] = agent
        agent.memory = self.shared_memory
        self.log(f"Registered professor agent: {agent.name} ({agent.agent_id})")
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process incoming message and route to appropriate professor agent
        """
        self.log(f"Processing professor request: {message.message_type} from {message.sender}")
        
        # Determine which agent should handle this request
        content = message.content
        request_type = content.get('type', '')
        action = content.get('action', '')
        
        # Route based on request type or action
        target_agent = self._route_to_agent(request_type, action)
        
        if not target_agent:
            return self.create_response(
                success=False,
                data={},
                error=f"No agent available to handle request type: {request_type}, action: {action}",
                confidence=0.0
            )
        
        # Forward message to target agent
        self.log(f"Routing to professor agent: {target_agent.name}")
        response = await target_agent.process(message)
        
        return response
    
    def _route_to_agent(self, request_type: str, action: str) -> Optional[BaseAgent]:
        """
        Route request to appropriate professor agent
        """
        # Routing map based on request type
        type_routing = {
            'clustering': 'clustering_agent',
            'clusters': 'clustering_agent',
            'canonical_answer': 'canonical_answer_agent',
            'canonical': 'canonical_answer_agent',
            'unresolved': 'unresolved_queue_agent',
            'unresolved_queue': 'unresolved_queue_agent',
            'dashboard': 'dashboard_agent',
            'metrics': 'dashboard_agent',
            'heatmap': 'dashboard_agent',
            'confusion': 'dashboard_agent',
            'students': 'dashboard_agent',
            'student_analytics': 'dashboard_agent',
            'content_gaps': 'dashboard_agent',
            'guardrails': 'guardrail_settings_agent',
            'guardrail_settings': 'guardrail_settings_agent',
        }
        
        # Action-based routing as fallback
        action_routing = {
            'get_clusters': 'clustering_agent',
            'get_semantic_clusters': 'clustering_agent',
            'suggest_cluster_name': 'clustering_agent',
            'log_question': 'clustering_agent',
            'create': 'canonical_answer_agent',  # Default for create is canonical
            'publish': 'canonical_answer_agent',
            'get_for_question': 'canonical_answer_agent',
            'find_by_similarity': 'canonical_answer_agent',
            'get_all_published': 'canonical_answer_agent',
            'get_queue': 'unresolved_queue_agent',
            'resolve': 'unresolved_queue_agent',
            'get_metrics': 'dashboard_agent',
            'get_confusion_heatmap': 'dashboard_agent',
            'get_student_analytics': 'dashboard_agent',
            'get_content_gaps': 'dashboard_agent',
            'log_confusion_signal': 'dashboard_agent',
            'get': 'guardrail_settings_agent',  # Context-dependent
            'update': 'guardrail_settings_agent',  # Context-dependent
        }
        
        # Try type-based routing first
        agent_id = type_routing.get(request_type.lower()) if request_type else None
        
        # Fallback to action-based routing
        if not agent_id and action:
            agent_id = action_routing.get(action.lower())
        
        return self.agents.get(agent_id) if agent_id else None
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered professor agents"""
        return {
            "orchestrator": "professor_orchestrator",
            "total_agents": len(self.agents),
            "agents": [
                {
                    "id": agent.agent_id,
                    "name": agent.name,
                    "capabilities": [cap.value for cap in agent.capabilities]
                }
                for agent in self.agents.values()
            ]
        }
    
    # Convenience methods for direct access (used by endpoints)
    async def get_dashboard_metrics(self, course_id: str = "cs50", days: int = 7) -> AgentResponse:
        """Get dashboard metrics"""
        message = self.create_message(
            receiver="dashboard_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'dashboard',
                'action': 'get_metrics',
                'course_id': course_id,
                'days': days
            }
        )
        return await self.process(message)
    
    async def get_student_analytics(self, course_id: str = "cs50") -> AgentResponse:
        """Get student analytics"""
        message = self.create_message(
            receiver="dashboard_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'students',
                'action': 'get_student_analytics',
                'course_id': course_id
            }
        )
        return await self.process(message)
    
    async def get_content_gaps(self, course_id: str = "cs50") -> AgentResponse:
        """Get content gaps"""
        message = self.create_message(
            receiver="dashboard_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'content_gaps',
                'action': 'get_content_gaps',
                'course_id': course_id
            }
        )
        return await self.process(message)
    
    async def get_question_clusters(self, course_id: str = "cs50", 
                                     min_count: int = 2, 
                                     semantic: bool = True) -> AgentResponse:
        """Get question clusters"""
        action = 'get_semantic_clusters' if semantic else 'get_clusters'
        message = self.create_message(
            receiver="clustering_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'clustering',
                'action': action,
                'course_id': course_id,
                'min_count': min_count
            }
        )
        return await self.process(message)
    
    async def create_canonical_answer(self, request_data: Dict[str, Any], 
                                       professor_id: str = "prof1") -> AgentResponse:
        """Create a canonical answer"""
        message = self.create_message(
            receiver="canonical_answer_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'canonical_answer',
                'action': 'create',
                'request': request_data,
                'professor_id': professor_id
            }
        )
        return await self.process(message)
    
    async def publish_canonical_answer(self, answer_id: str) -> AgentResponse:
        """Publish a canonical answer"""
        message = self.create_message(
            receiver="canonical_answer_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'canonical_answer',
                'action': 'publish',
                'answer_id': answer_id
            }
        )
        return await self.process(message)
    
    async def get_unresolved_queue(self, course_id: str = "cs50") -> AgentResponse:
        """Get unresolved queue"""
        message = self.create_message(
            receiver="unresolved_queue_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'unresolved',
                'action': 'get_queue',
                'course_id': course_id
            }
        )
        return await self.process(message)
    
    async def resolve_item(self, request_data: Dict[str, Any], 
                           professor_id: str = "prof1") -> AgentResponse:
        """Resolve an unresolved item"""
        message = self.create_message(
            receiver="unresolved_queue_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'unresolved',
                'action': 'resolve',
                'request': request_data,
                'professor_id': professor_id
            }
        )
        return await self.process(message)
    
    async def get_confusion_heatmap(self, course_id: str = "cs50", 
                                     days: int = 7) -> AgentResponse:
        """Get confusion heatmap"""
        message = self.create_message(
            receiver="dashboard_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'heatmap',
                'action': 'get_confusion_heatmap',
                'course_id': course_id,
                'days': days
            }
        )
        return await self.process(message)
    
    async def get_guardrail_settings(self, course_id: str = "cs50") -> AgentResponse:
        """Get guardrail settings"""
        message = self.create_message(
            receiver="guardrail_settings_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'guardrails',
                'action': 'get',
                'course_id': course_id
            }
        )
        return await self.process(message)
    
    async def update_guardrail_settings(self, course_id: str, request_data: Dict[str, Any],
                                         professor_id: str = "prof1") -> AgentResponse:
        """Update guardrail settings"""
        message = self.create_message(
            receiver="guardrail_settings_agent",
            message_type=MessageType.REQUEST,
            content={
                'type': 'guardrails',
                'action': 'update',
                'course_id': course_id,
                'request': request_data,
                'professor_id': professor_id
            }
        )
        return await self.process(message)
