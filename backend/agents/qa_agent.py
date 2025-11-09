"""
Q&A Agent - Refactored for Multi-Agent Framework
Answers course logistics and content questions with citations
"""
from typing import Dict, Any
import uuid
from datetime import datetime

from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import Citation, ChatResponse

class QAAgent(BaseAgent):
    """
    Specialized agent for answering course questions
    """
    
    def __init__(self):
        super().__init__(
            agent_id="qa_agent",
            name="Q&A Agent",
            capabilities=[AgentCapability.ANSWER_QUESTIONS, AgentCapability.RETRIEVE_DOCUMENTS]
        )
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process a Q&A request
        """
        try:
            content = message.content
            question = content.get('question', '')
            student_id = content.get('student_id', 'unknown')
            conversation_id = content.get('conversation_id', str(uuid.uuid4()))
            
            self.log(f"Processing Q&A: {question}")
            
            # Get conversation memory
            conversation = self.memory.get_or_create_conversation(conversation_id, student_id)
            conversation.add_turn("user", question)
            
            # Get student profile
            student_profile = self.memory.get_or_create_student_profile(student_id)
            
            # Use retrieval tool to get relevant documents
            retrieval_tool = self.get_tool("retrieval")
            if not retrieval_tool:
                return self.create_response(
                    success=False,
                    data={},
                    error="Retrieval tool not available",
                    confidence=0.0
                )
            
            retrieved_chunks = await retrieval_tool.execute({
                'query': question,
                'top_k': 3
            })
            
            if not retrieved_chunks:
                response_text = "I couldn't find relevant information in the course materials to answer your question."
                confidence = 0.0
                citations = []
                
                # Log confusion signal
                analytics_tool = self.get_tool("analytics")
                if analytics_tool:
                    await analytics_tool.execute({
                        'event_type': 'confusion',
                        'student_id': student_id,
                        'data': {
                            'question': question,
                            'artifact': 'unknown',
                            'signal_type': 'no_results'
                        }
                    })
            else:
                # Use citation tool to format citations
                citation_tool = self.get_tool("citation")
                citations = await citation_tool.execute({
                    'chunks': retrieved_chunks
                }) if citation_tool else []
                
                # Try to use OpenAI for better answers
                openai_tool = self.get_tool("openai")
                if openai_tool:
                    try:
                        # Prepare context from retrieved chunks
                        context = self._prepare_context(retrieved_chunks)
                        
                        # Generate answer using OpenAI
                        response_text = await openai_tool.execute({
                            'question': question,
                            'context': context,
                            'max_tokens': 500
                        })
                        confidence = 0.9  # Higher confidence with LLM
                        self.log("Generated answer using OpenAI")
                    except Exception as e:
                        self.log(f"OpenAI failed, using fallback: {str(e)}", "WARNING")
                        response_text = self._generate_answer(question, retrieved_chunks)
                        confidence = self._calculate_confidence(retrieved_chunks)
                else:
                    # Fallback to rule-based answer generation
                    response_text = self._generate_answer(question, retrieved_chunks)
                    confidence = self._calculate_confidence(retrieved_chunks)
                
                # Log the interaction
                analytics_tool = self.get_tool("analytics")
                if analytics_tool:
                    await analytics_tool.execute({
                        'event_type': 'question',
                        'student_id': student_id,
                        'data': {
                            'question': question,
                            'artifact': retrieved_chunks[0][0].source if retrieved_chunks else None,
                            'section': retrieved_chunks[0][0].section if retrieved_chunks else None,
                            'confidence': confidence,
                            'response': response_text
                        }
                    })
                
                # Update student profile
                topic = retrieved_chunks[0][0].section if retrieved_chunks else None
                student_profile.log_question(question, topic)
            
            # Add assistant response to conversation
            conversation.add_turn(self.agent_id, response_text)
            
            # Generate suggested follow-up questions
            suggested_questions = self._generate_suggested_questions(question, retrieved_chunks)
            
            # Create ChatResponse
            chat_response = ChatResponse(
                answer=response_text,
                citations=citations,
                confidence=confidence
            )
            
            return self.create_response(
                success=True,
                data={
                    'chat_response': chat_response.dict(),
                    'suggested_questions': suggested_questions,
                    'conversation_id': conversation_id
                },
                confidence=confidence,
                reasoning=f"Retrieved {len(retrieved_chunks)} relevant chunks"
            )
            
        except Exception as e:
            self.log(f"Error processing Q&A: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    def _prepare_context(self, retrieved_chunks) -> str:
        """Prepare context from retrieved chunks for OpenAI"""
        context_parts = []
        for i, (chunk, score) in enumerate(retrieved_chunks):
            context_parts.append(f"[Source {i+1}: {chunk.source} - {chunk.section}]\n{chunk.text}\n")
        return "\n".join(context_parts)
    
    def _generate_answer(self, question: str, retrieved_chunks) -> str:
        """Generate answer based on question type"""
        if not retrieved_chunks:
            return "I don't have enough information to answer that question."
        
        question_lower = question.lower()
        top_chunk = retrieved_chunks[0][0]
        
        # Deadline questions
        if any(word in question_lower for word in ['when', 'due', 'deadline', 'date']):
            return self._format_deadline_answer(top_chunk, question)
        
        # Policy questions
        elif any(word in question_lower for word in ['policy', 'rule', 'allowed', 'can i']):
            return self._format_policy_answer(top_chunk)
        
        # Support questions
        elif any(word in question_lower for word in ['office hours', 'help', 'support', 'contact']):
            return self._format_support_answer(top_chunk)
        
        # General questions
        else:
            return self._format_general_answer(top_chunk)
    
    def _format_deadline_answer(self, chunk, question: str) -> str:
        """Format deadline-specific answer"""
        text = chunk.text.strip()
        
        if 'due date' in chunk.section.lower():
            return f"📅 **{chunk.section}**\n\n{text}\n\n[Source: {chunk.source} - {chunk.section}]"
        
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['due', 'deadline', 'september', 'october', 'november', 'december']):
                return f"📅 {line.strip()}\n\n[Source: {chunk.source} - {chunk.section}]"
        
        return f"📅 According to the course materials:\n\n{text[:200]}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_policy_answer(self, chunk) -> str:
        """Format policy-specific answer"""
        return f"📋 **Policy Information**\n\n{chunk.text}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_support_answer(self, chunk) -> str:
        """Format support-specific answer"""
        return f"🤝 **Support & Resources**\n\n{chunk.text}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_general_answer(self, chunk) -> str:
        """Format general answer"""
        return f"{chunk.text}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _calculate_confidence(self, retrieved_chunks) -> float:
        """Calculate confidence score based on retrieval scores"""
        if not retrieved_chunks:
            return 0.0
        
        top_score = retrieved_chunks[0][1]
        return min(top_score, 0.95)
    
    def _generate_suggested_questions(self, question: str, retrieved_chunks) -> list:
        """Generate contextual follow-up questions"""
        if not retrieved_chunks:
            return [
                'What is the late policy?',
                'When are office hours?',
                'How do I submit assignments?'
            ]
        
        chunk = retrieved_chunks[0][0]
        
        if 'assignment' in chunk.source.lower():
            return [
                'What is the grading policy?',
                'Can I work with others?',
                'When is this due?'
            ]
        elif 'syllabus' in chunk.source.lower():
            return [
                'Tell me about the grading policy',
                'What are the office hours?',
                'When is Problem Set 2 due?'
            ]
        
        return [
            'Tell me about the grading policy',
            'What are the office hours?',
            'When is Problem Set 2 due?'
        ]
