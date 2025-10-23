"""
Hybrid retrieval: BM25 + semantic embeddings
"""
from typing import List, Tuple
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.metrics.pairwise import cosine_similarity
from document_store import DocumentChunk

class HybridRetriever:
    """Combines BM25 and semantic search for retrieval"""
    
    def __init__(self):
        self.chunks: List[DocumentChunk] = []
        self.bm25 = None
        self.embeddings = None
        
    def index_chunks(self, chunks: List[DocumentChunk]):
        """Index chunks for retrieval"""
        self.chunks = chunks
        
        # BM25 indexing
        tokenized_chunks = [chunk.text.lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(tokenized_chunks)
        
        # Generate embeddings (simulated for MVP - in production use OpenAI embeddings)
        print("Generating embeddings for chunks...")
        self.embeddings = self._generate_embeddings([chunk.text for chunk in chunks])
        print(f"Indexed {len(chunks)} chunks")
    
    def _generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts using simple TF-IDF-like approach.
        For MVP: using simulated embeddings for demonstration.
        """
        # Simulated embeddings for MVP (random but consistent with seed)
        np.random.seed(hash(texts[0]) % 2**32)
        return np.random.rand(len(texts), 384)
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Tuple[DocumentChunk, float]]:
        """
        Retrieve top-k most relevant chunks using hybrid search
        Returns: List of (chunk, score) tuples
        """
        if not self.chunks:
            return []
        
        # BM25 scores
        tokenized_query = query.lower().split()
        bm25_scores = self.bm25.get_scores(tokenized_query)
        
        # Semantic scores (simulated)
        query_embedding = self._generate_embeddings([query])[0]
        semantic_scores = cosine_similarity([query_embedding], self.embeddings)[0]
        
        # Adjust weights based on query type
        # For specific queries (dates, deadlines), favor keyword matching
        query_lower = query.lower()
        if any(word in query_lower for word in ['when', 'due', 'deadline', 'date']):
            bm25_weight = 0.7  # Higher weight for keyword matching
            semantic_weight = 0.3
        elif any(word in query_lower for word in ['what', 'how', 'why']):
            bm25_weight = 0.5
            semantic_weight = 0.5
        else:
            bm25_weight = 0.4
            semantic_weight = 0.6
        
        # Normalize scores to 0-1 range
        bm25_scores_norm = (bm25_scores - bm25_scores.min()) / (bm25_scores.max() - bm25_scores.min() + 1e-10)
        semantic_scores_norm = (semantic_scores - semantic_scores.min()) / (semantic_scores.max() - semantic_scores.min() + 1e-10)
        
        combined_scores = bm25_weight * bm25_scores_norm + semantic_weight * semantic_scores_norm
        
        # Get top-k indices
        top_indices = np.argsort(combined_scores)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            results.append((self.chunks[idx], float(combined_scores[idx])))
        
        return results
