"""
Retrieval Tool
Searches and retrieves relevant documents
"""
from typing import Dict, Any, List, Tuple
from .base_tool import BaseTool
from document_store import DocumentChunk

class RetrievalTool(BaseTool):
    """
    Tool for retrieving relevant documents from the knowledge base
    """
    
    def __init__(self, retriever):
        super().__init__(
            name="retrieval",
            description="Search and retrieve relevant documents from course materials"
        )
        self.retriever = retriever
    
    async def execute(self, params: Dict[str, Any]) -> List[Tuple[DocumentChunk, float]]:
        """
        Execute document retrieval
        
        Params:
            query (str): Search query
            top_k (int): Number of results to return (default: 3)
        """
        if not self.validate_params(params, ['query']):
            raise ValueError("Missing required parameter: query")
        
        query = params['query']
        top_k = params.get('top_k', 3)
        
        # Use the retriever to get relevant chunks
        results = self.retriever.retrieve(query, top_k=top_k)
        
        return results
