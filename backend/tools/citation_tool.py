"""
Citation Tool
Formats and validates citations
"""
from typing import Dict, Any, List
from .base_tool import BaseTool
from models import Citation
from document_store import DocumentChunk

class CitationTool(BaseTool):
    """
    Tool for creating and validating citations
    """
    
    def __init__(self):
        super().__init__(
            name="citation",
            description="Format and validate citations from retrieved documents"
        )
    
    async def execute(self, params: Dict[str, Any]) -> List[Citation]:
        """
        Create citations from retrieved chunks
        
        Params:
            chunks (List[Tuple[DocumentChunk, float]]): Retrieved chunks with scores
            max_length (int): Maximum citation text length (default: 500)
        """
        if not self.validate_params(params, ['chunks']):
            raise ValueError("Missing required parameter: chunks")
        
        chunks = params['chunks']
        max_length = params.get('max_length', 500)
        
        citations = []
        for chunk, score in chunks:
            citation_text = self._format_citation_text(chunk.text, max_length)
            
            citations.append(Citation(
                source=chunk.source,
                section=chunk.section,
                text=citation_text,
                relevance_score=score
            ))
        
        return citations
    
    def _format_citation_text(self, text: str, max_length: int) -> str:
        """Format citation text with smart truncation"""
        if len(text) <= max_length:
            return text
        
        # Try to cut at sentence boundary
        truncated = text[:max_length]
        last_period = truncated.rfind('.')
        
        if last_period > max_length * 0.6:  # If sentence ending is in reasonable range
            return text[:last_period + 1] + "..."
        else:
            return truncated + "..."
