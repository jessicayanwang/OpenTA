"""
Orchestrator Agent
Routes requests to appropriate specialized agents and coordinates multi-agent workflows
"""
from typing import Dict, Any, List, Optional
import re
from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse, MessageType
from memory.shared_memory import SharedMemory

class OrchestratorAgent(BaseAgent):
    """
    Main orchestrator that routes requests to appropriate agents
    """
    
    def __init__(self, shared_memory: SharedMemory):
        super().__init__(
            agent_id="orchestrator",
            name="Orchestrator Agent",
            capabilities=[]  # Orchestrator doesn't have specific capabilities
        )
        self.shared_memory = shared_memory
        self.agents: Dict[str, BaseAgent] = {}
        
    def register_agent(self, agent: BaseAgent):
        """Register a specialized agent"""
        self.agents[agent.agent_id] = agent
        agent.memory = self.shared_memory
        self.log(f"Registered agent: {agent.name} ({agent.agent_id})")
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process incoming message and route to appropriate agent
        """
        self.log(f"Processing message: {message.message_type} from {message.sender}")
        
        # Extract intent from message
        intent = self._classify_intent(message.content)
        self.log(f"Classified intent: {intent}")
        
        # Route to appropriate agent
        target_agent = self._route_to_agent(intent)
        
        if not target_agent:
            return self.create_response(
                success=False,
                data={},
                error=f"No agent available to handle intent: {intent}",
                confidence=0.0
            )
        
        # Forward message to target agent
        self.log(f"Routing to agent: {target_agent.name}")
        response = await target_agent.process(message)
        
        return response
    
    def _classify_intent(self, content: Dict[str, Any]) -> str:
        """
        Classify the intent of the user's request
        """
        question = content.get('question', '').lower()
        request_type = content.get('type', '')
        
        # Explicit type specified
        if request_type:
            return request_type
        
        # Pattern matching for intent classification
        
        # Assignment help patterns
        assignment_patterns = [
            r'stuck on',
            r'help with.*problem',
            r'how do i.*implement',
            r'can you help.*assignment',
            r'hint',
            r'mario',
            r'caesar',
            r'problem set'
        ]
        
        for pattern in assignment_patterns:
            if re.search(pattern, question):
                return 'assignment_help'
        
        # Study plan patterns
        study_patterns = [
            r'study plan',
            r'how should i study',
            r'prepare for.*exam',
            r'schedule',
            r'study schedule'
        ]
        
        for pattern in study_patterns:
            if re.search(pattern, question):
                return 'study_plan'
        
        # Default to Q&A for course logistics
        return 'qa'
    
    def _route_to_agent(self, intent: str) -> Optional[BaseAgent]:
        """
        Route intent to appropriate agent
        """
        routing_map = {
            'qa': 'qa_agent',
            'assignment_help': 'assignment_helper',
            'study_plan': 'study_plan_agent'
        }
        
        agent_id = routing_map.get(intent)
        return self.agents.get(agent_id) if agent_id else None
    
    async def handle_multi_agent_task(self, message: AgentMessage) -> AgentResponse:
        """
        Handle complex tasks that require multiple agents
        (Future enhancement)
        """
        # TODO: Implement multi-agent coordination
        pass
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all registered agents"""
        return {
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
