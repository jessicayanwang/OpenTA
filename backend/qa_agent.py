"""
Q&A Agent with hardcoded rule-based responses and citations
Simple MVP without LLM dependency
"""
from typing import List, Tuple
from document_store import DocumentChunk
from models import Citation, ChatResponse

class QAAgent:
    """Generates grounded answers with citations using simple rules"""
    
    def __init__(self):
        pass
    
    def generate_answer(
        self, 
        question: str, 
        retrieved_chunks: List[Tuple[DocumentChunk, float]]
    ) -> ChatResponse:
        """
        Generate an answer based on retrieved chunks with citations
        """
        if not retrieved_chunks:
            return ChatResponse(
                answer="I don't have enough information to answer that question. Please check the course materials or contact the instructor.",
                citations=[],
                confidence=0.0
            )
        
        # Build citations from retrieved chunks
        citations = []
        
        for i, (chunk, score) in enumerate(retrieved_chunks):
            # Show full text for short chunks, or up to 500 chars for longer ones
            citation_text = chunk.text
            if len(chunk.text) > 500:
                # Try to cut at a sentence boundary
                truncated = chunk.text[:500]
                last_period = truncated.rfind('.')
                if last_period > 300:  # If there's a sentence ending in reasonable range
                    citation_text = chunk.text[:last_period + 1] + "..."
                else:
                    citation_text = truncated + "..."
            
            citations.append(Citation(
                source=chunk.source,
                section=chunk.section,
                text=citation_text,
                relevance_score=score
            ))
        
        # Generate answer using simple rule-based approach
        answer = self._generate_answer_from_chunks(question, retrieved_chunks)
        confidence = 0.75
        
        return ChatResponse(
            answer=answer,
            citations=citations,
            confidence=confidence
        )
    
    def _generate_answer_from_chunks(
        self, 
        question: str, 
        retrieved_chunks: List[Tuple[DocumentChunk, float]]
    ) -> str:
        """Generate answer from retrieved chunks using simple rules"""
        
        # Get the most relevant chunk
        top_chunk, top_score = retrieved_chunks[0]
        
        # Detect question type and format accordingly
        q_lower = question.lower()
        
        if 'when' in q_lower and ('due' in q_lower or 'deadline' in q_lower):
            # Date/deadline question
            answer = self._format_deadline_answer(top_chunk, question)
        elif 'what' in q_lower and 'policy' in q_lower:
            # Policy question
            answer = self._format_policy_answer(top_chunk, question)
        elif 'office hours' in q_lower or 'help' in q_lower:
            # Support question
            answer = self._format_support_answer(top_chunk, question)
        elif 'problem' in q_lower or 'assignment' in q_lower:
            # Assignment question
            answer = self._format_assignment_answer(top_chunk, question)
        else:
            # General question
            answer = self._format_general_answer(top_chunk, question)
        
        return answer
    
    def _format_deadline_answer(self, chunk: DocumentChunk, question: str) -> str:
        text = chunk.text.strip()
        
        # If the section is specifically about due dates, use it directly
        if 'due date' in chunk.section.lower():
            return f"📅 **{chunk.section}**\n\n{text}\n\n[Source: {chunk.source} - {chunk.section}]"
        
        # Extract date if present in text
        lines = text.split('\n')
        for line in lines:
            if any(word in line.lower() for word in ['due', 'deadline', 'september', 'october', 'november', 'december']):
                return f"📅 {line.strip()}\n\n[Source: {chunk.source} - {chunk.section}]"
        
        return f"📅 According to the course materials:\n\n{text[:200]}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_policy_answer(self, chunk: DocumentChunk, question: str) -> str:
        text = chunk.text.strip()
        return f"📋 Here's the policy:\n\n{text}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_support_answer(self, chunk: DocumentChunk, question: str) -> str:
        text = chunk.text.strip()
        return f"🤝 Support Information:\n\n{text}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_assignment_answer(self, chunk: DocumentChunk, question: str) -> str:
        text = chunk.text.strip()
        return f"📝 Assignment Details:\n\n{text}\n\n[Source: {chunk.source} - {chunk.section}]"
    
    def _format_general_answer(self, chunk: DocumentChunk, question: str) -> str:
        text = chunk.text.strip()
        return f"Based on the course materials:\n\n{text}\n\n[Source: {chunk.source} - {chunk.section}]"
