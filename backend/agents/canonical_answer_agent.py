"""
Canonical Answer Agent
Manages canonical answers for question clusters
"""
from typing import Dict, Any

from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import CreateCanonicalAnswerRequest


class CanonicalAnswerAgent(BaseAgent):
    """
    Specialized agent for managing canonical answers
    """
    
    def __init__(self, professor_service):
        super().__init__(
            agent_id="canonical_answer_agent",
            name="Canonical Answer Agent",
            capabilities=[AgentCapability.MANAGE_CANONICAL_ANSWERS]
        )
        self.professor_service = professor_service
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process a canonical answer management request
        """
        try:
            content = message.content
            action = content.get('action', 'create')
            professor_id = content.get('professor_id', 'prof1')
            
            self.log(f"Processing canonical answer action: {action}")
            
            if action == 'create':
                return await self._create_answer(content, professor_id)
            elif action == 'publish':
                return await self._publish_answer(content)
            elif action == 'get_for_question':
                return await self._get_for_question(content)
            elif action == 'find_by_similarity':
                return await self._find_by_similarity(content)
            elif action == 'get_all_published':
                return await self._get_all_published()
            else:
                return self.create_response(
                    success=False,
                    data={},
                    error=f"Unknown action: {action}",
                    confidence=0.0
                )
                
        except Exception as e:
            self.log(f"Error processing canonical answer request: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _create_answer(self, content: Dict[str, Any], professor_id: str) -> AgentResponse:
        """Create a new canonical answer"""
        request_data = content.get('request')
        if not request_data:
            return self.create_response(
                success=False,
                data={},
                error="Missing request data",
                confidence=0.0
            )
        
        # Convert dict to CreateCanonicalAnswerRequest
        if isinstance(request_data, dict):
            request = CreateCanonicalAnswerRequest(**request_data)
        else:
            request = request_data
        
        canonical = self.professor_service.create_canonical_answer(request, professor_id)
        
        return self.create_response(
            success=True,
            data={'canonical_answer': canonical.dict()},
            confidence=1.0,
            reasoning=f"Created canonical answer for cluster {request.cluster_id}"
        )
    
    async def _publish_answer(self, content: Dict[str, Any]) -> AgentResponse:
        """Publish a canonical answer"""
        answer_id = content.get('answer_id')
        if not answer_id:
            return self.create_response(
                success=False,
                data={},
                error="Missing answer_id",
                confidence=0.0
            )
        
        try:
            canonical = self.professor_service.publish_canonical_answer(answer_id)
            return self.create_response(
                success=True,
                data={'canonical_answer': canonical.dict()},
                confidence=1.0,
                reasoning=f"Published canonical answer {answer_id}"
            )
        except ValueError as e:
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _get_for_question(self, content: Dict[str, Any]) -> AgentResponse:
        """Get canonical answer for a specific question"""
        question = content.get('question', '')
        artifact = content.get('artifact')
        section = content.get('section')
        
        canonical = self.professor_service.get_canonical_answer_for_question(
            question, artifact, section
        )
        
        if canonical:
            return self.create_response(
                success=True,
                data={'canonical_answer': canonical.dict(), 'found': True},
                confidence=1.0,
                reasoning="Found matching canonical answer"
            )
        else:
            return self.create_response(
                success=True,
                data={'canonical_answer': None, 'found': False},
                confidence=1.0,
                reasoning="No matching canonical answer found"
            )
    
    async def _find_by_similarity(self, content: Dict[str, Any]) -> AgentResponse:
        """Find canonical answer using semantic similarity"""
        question = content.get('question', '')
        similarity_threshold = content.get('similarity_threshold', 0.75)
        
        canonical = self.professor_service.find_canonical_answer(
            question, similarity_threshold
        )
        
        if canonical:
            return self.create_response(
                success=True,
                data={'canonical_answer': canonical.dict(), 'found': True},
                confidence=0.9,
                reasoning="Found semantically similar canonical answer"
            )
        else:
            return self.create_response(
                success=True,
                data={'canonical_answer': None, 'found': False},
                confidence=1.0,
                reasoning="No semantically similar canonical answer found"
            )
    
    async def _get_all_published(self) -> AgentResponse:
        """Get all published canonical answers"""
        answers = self.professor_service.get_all_published_canonical_answers()
        
        return self.create_response(
            success=True,
            data={
                'canonical_answers': [a.dict() for a in answers],
                'total_count': len(answers)
            },
            confidence=1.0,
            reasoning=f"Retrieved {len(answers)} published canonical answers"
        )
