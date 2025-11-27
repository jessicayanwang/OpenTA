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
            min_score (float): Minimum relevance score to include (default: 0.5)
            max_citations (int): Maximum number of citations to return (default: 2)
        """
        if not self.validate_params(params, ['chunks']):
            raise ValueError("Missing required parameter: chunks")
        
        chunks = params['chunks']
        max_length = params.get('max_length', 500)
        min_score = params.get('min_score', 0.5)
        max_citations = params.get('max_citations', 2)
        
        citations = []
        seen_sources = set()  # Avoid duplicate sources
        
        for chunk, score in chunks:
            # Skip low-relevance chunks
            if score < min_score:
                continue
            
            # Skip duplicate sources (keep only first occurrence)
            source_key = f"{chunk.source}::{chunk.section}"
            if source_key in seen_sources:
                continue
            seen_sources.add(source_key)
            
            citation_text = self._format_citation_text(chunk.text, max_length)
            
            citations.append(Citation(
                source=chunk.source,
                section=chunk.section,
                text=citation_text,
                relevance_score=score
            ))
            
            # Limit number of citations
            if len(citations) >= max_citations:
                break
        
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
