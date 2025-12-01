"""
Clustering Agent
Handles question clustering and semantic analysis for the professor dashboard
"""
from typing import Dict, Any

from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import QuestionCluster


class ClusteringAgent(BaseAgent):
    """
    Specialized agent for question clustering and semantic analysis
    """
    
    def __init__(self, professor_service):
        super().__init__(
            agent_id="clustering_agent",
            name="Clustering Agent",
            capabilities=[AgentCapability.CLUSTER_QUESTIONS]
        )
        self.professor_service = professor_service
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process a clustering request
        """
        try:
            content = message.content
            action = content.get('action', 'get_clusters')
            course_id = content.get('course_id', 'cs50')
            
            self.log(f"Processing clustering action: {action}")
            
            if action == 'get_clusters':
                return await self._get_clusters(content, course_id)
            elif action == 'get_semantic_clusters':
                return await self._get_semantic_clusters(content, course_id)
            elif action == 'suggest_cluster_name':
                return await self._suggest_cluster_name(content)
            elif action == 'log_question':
                return await self._log_question(content)
            else:
                return self.create_response(
                    success=False,
                    data={},
                    error=f"Unknown action: {action}",
                    confidence=0.0
                )
                
        except Exception as e:
            self.log(f"Error processing clustering request: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _get_clusters(self, content: Dict[str, Any], course_id: str) -> AgentResponse:
        """Get question clusters using simple keyword-based clustering"""
        min_count = content.get('min_count', 2)
        
        clusters = self.professor_service.get_question_clusters(course_id, min_count)
        
        # Enrich clusters with canonical answer text if available
        from database import CanonicalAnswerDB
        session = self.professor_service.db.get_session()
        try:
            enriched_clusters = []
            answered_count = 0
            for c in clusters:
                cluster_dict = c.model_dump()
                if c.canonical_answer_id:
                    answered_count += 1
                    print(f"🔍 Enriching cluster {c.cluster_id} with canonical answer {c.canonical_answer_id}")
                    canonical = session.query(CanonicalAnswerDB).filter_by(
                        answer_id=c.canonical_answer_id
                    ).first()
                    if canonical:
                        cluster_dict['canonical_answer'] = canonical.answer_markdown
                        cluster_dict['last_updated'] = canonical.updated_at.strftime('%Y-%m-%d')
                        print(f"✅ Added canonical answer text to cluster {c.cluster_id}")
                    else:
                        print(f"❌ WARNING: Canonical answer {c.canonical_answer_id} not found!")
                enriched_clusters.append(cluster_dict)
            
            print(f"📊 _get_clusters: Returning {len(enriched_clusters)} clusters ({answered_count} answered)")
        finally:
            session.close()
        
        return self.create_response(
            success=True,
            data={
                'clusters': enriched_clusters,
                'total_count': len(clusters)
            },
            confidence=1.0,
            reasoning=f"Retrieved {len(clusters)} clusters with min_count={min_count}"
        )
    
    async def _get_semantic_clusters(self, content: Dict[str, Any], course_id: str) -> AgentResponse:
        """Get question clusters using semantic similarity (embeddings)"""
        min_count = content.get('min_count', 2)
        similarity_threshold = content.get('similarity_threshold', 0.7)
        
        clusters = self.professor_service.get_semantic_clusters(
            course_id, 
            similarity_threshold=similarity_threshold, 
            min_count=min_count
        )
        
        # Enrich clusters with canonical answer text if available
        from database import CanonicalAnswerDB
        session = self.professor_service.db.get_session()
        try:
            enriched_clusters = []
            answered_count = 0
            for c in clusters:
                cluster_dict = c.model_dump()
                if c.canonical_answer_id:
                    answered_count += 1
                    print(f"🔍 Enriching cluster {c.cluster_id} with canonical answer {c.canonical_answer_id}")
                    canonical = session.query(CanonicalAnswerDB).filter_by(
                        answer_id=c.canonical_answer_id
                    ).first()
                    if canonical:
                        cluster_dict['canonical_answer'] = canonical.answer_markdown
                        cluster_dict['last_updated'] = canonical.updated_at.strftime('%Y-%m-%d')
                        print(f"✅ Added canonical answer text to cluster {c.cluster_id}")
                    else:
                        print(f"❌ WARNING: Canonical answer {c.canonical_answer_id} not found!")
                enriched_clusters.append(cluster_dict)
            
            print(f"📊 _get_semantic_clusters: Returning {len(enriched_clusters)} clusters ({answered_count} answered)")
        finally:
            session.close()
        
        return self.create_response(
            success=True,
            data={
                'clusters': enriched_clusters,
                'total_count': len(clusters),
                'similarity_threshold': similarity_threshold
            },
            confidence=1.0,
            reasoning=f"Retrieved {len(clusters)} semantic clusters"
        )
    
    async def _suggest_cluster_name(self, content: Dict[str, Any]) -> AgentResponse:
        """Suggest a descriptive name for a cluster"""
        cluster_data = content.get('cluster')
        if not cluster_data:
            return self.create_response(
                success=False,
                data={},
                error="Missing cluster data",
                confidence=0.0
            )
        
        # Convert dict to QuestionCluster if needed
        if isinstance(cluster_data, dict):
            cluster = QuestionCluster(**cluster_data)
        else:
            cluster = cluster_data
        
        suggested_name = self.professor_service.suggest_cluster_name(cluster)
        
        return self.create_response(
            success=True,
            data={'suggested_name': suggested_name},
            confidence=0.8,
            reasoning="Generated cluster name based on question patterns"
        )
    
    async def _log_question(self, content: Dict[str, Any]) -> AgentResponse:
        """Log a student question for clustering analysis"""
        student_id = content.get('student_id', 'unknown')
        question = content.get('question', '')
        artifact = content.get('artifact')
        section = content.get('section')
        confidence = content.get('confidence', 1.0)
        response = content.get('response', '')
        
        self.professor_service.log_question(
            student_id=student_id,
            question=question,
            artifact=artifact,
            section=section,
            confidence=confidence,
            response=response
        )
        
        return self.create_response(
            success=True,
            data={'logged': True},
            confidence=1.0,
            reasoning="Question logged for clustering"
        )
