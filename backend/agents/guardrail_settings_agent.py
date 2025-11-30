"""
Guardrail Settings Agent
Manages guardrail settings for the course
"""
from typing import Dict, Any

from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import UpdateGuardrailRequest


class GuardrailSettingsAgent(BaseAgent):
    """
    Specialized agent for managing guardrail settings
    """
    
    def __init__(self, professor_service):
        super().__init__(
            agent_id="guardrail_settings_agent",
            name="Guardrail Settings Agent",
            capabilities=[AgentCapability.MANAGE_GUARDRAILS]
        )
        self.professor_service = professor_service
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process a guardrail settings request
        """
        try:
            content = message.content
            action = content.get('action', 'get')
            course_id = content.get('course_id', 'cs50')
            professor_id = content.get('professor_id', 'prof1')
            
            self.log(f"Processing guardrail settings action: {action}")
            
            if action == 'get':
                return await self._get_settings(course_id)
            elif action == 'update':
                return await self._update_settings(content, course_id, professor_id)
            else:
                return self.create_response(
                    success=False,
                    data={},
                    error=f"Unknown action: {action}",
                    confidence=0.0
                )
                
        except Exception as e:
            self.log(f"Error processing guardrail settings request: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _get_settings(self, course_id: str) -> AgentResponse:
        """Get guardrail settings for a course"""
        settings = self.professor_service.get_guardrail_settings(course_id)
        
        return self.create_response(
            success=True,
            data={'settings': settings.dict()},
            confidence=1.0,
            reasoning=f"Retrieved guardrail settings for course {course_id}"
        )
    
    async def _update_settings(self, content: Dict[str, Any], course_id: str, 
                               professor_id: str) -> AgentResponse:
        """Update guardrail settings"""
        request_data = content.get('request')
        if not request_data:
            return self.create_response(
                success=False,
                data={},
                error="Missing request data",
                confidence=0.0
            )
        
        # Convert dict to UpdateGuardrailRequest
        if isinstance(request_data, dict):
            request = UpdateGuardrailRequest(**request_data)
        else:
            request = request_data
        
        settings = self.professor_service.update_guardrail_settings(
            course_id, request, professor_id
        )
        
        return self.create_response(
            success=True,
            data={'settings': settings.dict()},
            confidence=1.0,
            reasoning=f"Updated guardrail settings for course {course_id}"
        )
