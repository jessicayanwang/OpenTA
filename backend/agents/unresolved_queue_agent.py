"""
Unresolved Queue Agent
Manages the unresolved questions queue for professor review
"""
from typing import Dict, Any

from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import ResolveItemRequest


class UnresolvedQueueAgent(BaseAgent):
    """
    Specialized agent for managing the unresolved questions queue
    """
    
    def __init__(self, professor_service):
        super().__init__(
            agent_id="unresolved_queue_agent",
            name="Unresolved Queue Agent",
            capabilities=[AgentCapability.MANAGE_UNRESOLVED_QUEUE]
        )
        self.professor_service = professor_service
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process an unresolved queue management request
        """
        try:
            content = message.content
            action = content.get('action', 'get_queue')
            course_id = content.get('course_id', 'cs50')
            professor_id = content.get('professor_id', 'prof1')
            
            self.log(f"Processing unresolved queue action: {action}")
            
            if action == 'get_queue':
                return await self._get_queue(course_id)
            elif action == 'resolve':
                return await self._resolve_item(content, professor_id)
            else:
                return self.create_response(
                    success=False,
                    data={},
                    error=f"Unknown action: {action}",
                    confidence=0.0
                )
                
        except Exception as e:
            self.log(f"Error processing unresolved queue request: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _get_queue(self, course_id: str) -> AgentResponse:
        """Get all unresolved items"""
        items = self.professor_service.get_unresolved_queue(course_id)
        
        return self.create_response(
            success=True,
            data={
                'unresolved_items': [item.dict() for item in items],
                'total_count': len(items)
            },
            confidence=1.0,
            reasoning=f"Retrieved {len(items)} unresolved items"
        )
    
    async def _resolve_item(self, content: Dict[str, Any], professor_id: str) -> AgentResponse:
        """Resolve an unresolved queue item"""
        request_data = content.get('request')
        if not request_data:
            return self.create_response(
                success=False,
                data={},
                error="Missing request data",
                confidence=0.0
            )
        
        # Convert dict to ResolveItemRequest
        if isinstance(request_data, dict):
            request = ResolveItemRequest(**request_data)
        else:
            request = request_data
        
        try:
            item = self.professor_service.resolve_item(request, professor_id)
            return self.create_response(
                success=True,
                data={'resolved_item': item.dict()},
                confidence=1.0,
                reasoning=f"Resolved item {request.item_id}"
            )
        except ValueError as e:
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
