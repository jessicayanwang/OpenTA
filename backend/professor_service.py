"""
Professor Console Service
Handles question clustering, unresolved queue, confusion tracking, and guardrail settings
"""
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from models import (
    QuestionCluster, CanonicalAnswer, CreateCanonicalAnswerRequest,
    UnresolvedItem, UnresolvedReason, ResolveItemRequest,
    ConfusionSignal, ConfusionHeatmapEntry,
    GuardrailSettings, UpdateGuardrailRequest,
    Citation
)

class ProfessorService:
    """Manages professor console features"""
    
    def __init__(self, embedder=None):
        # In-memory storage (would be database in production)
        self.question_logs: List[Dict] = []  # All student questions
        self.clusters: Dict[str, QuestionCluster] = {}
        self.canonical_answers: Dict[str, CanonicalAnswer] = {}
        self.unresolved_queue: Dict[str, UnresolvedItem] = {}
        self.confusion_signals: List[ConfusionSignal] = []
        self.guardrail_settings: Dict[str, GuardrailSettings] = {}
        self.embedder = embedder  # For semantic clustering
        
    # Question Clustering
    def log_question(self, student_id: str, question: str, artifact: Optional[str], 
                    section: Optional[str], confidence: float, response: str):
        """Log a student question for clustering analysis"""
        log_entry = {
            "student_id": student_id,
            "question": question,
            "artifact": artifact,
            "section": section,
            "confidence": confidence,
            "response": response,
            "timestamp": datetime.now()
        }
        self.question_logs.append(log_entry)
        
        # Check if should add to unresolved queue
        if confidence < 0.6:
            self._add_to_unresolved(student_id, question, artifact, section, 
                                   UnresolvedReason.LOW_CONFIDENCE, confidence, response)
        
        # Simple clustering by artifact+section
        self._update_clusters(question, artifact, section)
        
    def _update_clusters(self, question: str, artifact: Optional[str], section: Optional[str]):
        """Simple clustering based on artifact and section"""
        cluster_key = f"{artifact or 'general'}_{section or 'general'}"
        
        if cluster_key in self.clusters:
            cluster = self.clusters[cluster_key]
            cluster.similar_questions.append(question)
            cluster.count += 1
            cluster.last_seen = datetime.now()
        else:
            cluster_id = str(uuid.uuid4())
            self.clusters[cluster_key] = QuestionCluster(
                cluster_id=cluster_id,
                representative_question=question,
                similar_questions=[question],
                count=1,
                artifact=artifact,
                section=section,
                created_at=datetime.now(),
                last_seen=datetime.now()
            )
    
    def get_question_clusters(self, course_id: str, min_count: int = 2) -> List[QuestionCluster]:
        """Get all question clusters with at least min_count questions"""
        clusters = [c for c in self.clusters.values() if c.count >= min_count]
        # Sort by count descending
        return sorted(clusters, key=lambda x: x.count, reverse=True)
    
    def create_canonical_answer(self, request: CreateCanonicalAnswerRequest, 
                               professor_id: str) -> CanonicalAnswer:
        """Create a canonical answer for a question cluster"""
        answer_id = str(uuid.uuid4())
        now = datetime.now()
        
        canonical = CanonicalAnswer(
            answer_id=answer_id,
            cluster_id=request.cluster_id,
            question=request.question,
            answer_markdown=request.answer_markdown,
            citations=request.citations,
            created_by=professor_id,
            created_at=now,
            updated_at=now,
            is_published=False
        )
        
        self.canonical_answers[answer_id] = canonical
        
        # Link to cluster
        for cluster in self.clusters.values():
            if cluster.cluster_id == request.cluster_id:
                cluster.canonical_answer_id = answer_id
                break
        
        return canonical
    
    def publish_canonical_answer(self, answer_id: str) -> CanonicalAnswer:
        """Publish a canonical answer to make it available to students"""
        if answer_id in self.canonical_answers:
            self.canonical_answers[answer_id].is_published = True
            self.canonical_answers[answer_id].updated_at = datetime.now()
            return self.canonical_answers[answer_id]
        raise ValueError(f"Canonical answer {answer_id} not found")
    
    def get_canonical_answer_for_question(self, question: str, artifact: Optional[str], 
                                         section: Optional[str]) -> Optional[CanonicalAnswer]:
        """Check if there's a published canonical answer for this question"""
        cluster_key = f"{artifact or 'general'}_{section or 'general'}"
        
        if cluster_key in self.clusters:
            cluster = self.clusters[cluster_key]
            if cluster.canonical_answer_id:
                answer = self.canonical_answers.get(cluster.canonical_answer_id)
                if answer and answer.is_published:
                    return answer
        return None
    
    # Unresolved Queue
    def _add_to_unresolved(self, student_id: str, question: str, artifact: Optional[str],
                          section: Optional[str], reason: UnresolvedReason, 
                          confidence: Optional[float], response: Optional[str]):
        """Add item to unresolved queue"""
        item_id = str(uuid.uuid4())
        
        item = UnresolvedItem(
            item_id=item_id,
            student_question=question,
            student_id=student_id,
            artifact=artifact,
            section=section,
            reason=reason,
            confidence=confidence,
            generated_response=response,
            created_at=datetime.now()
        )
        
        self.unresolved_queue[item_id] = item
    
    def get_unresolved_queue(self, course_id: str) -> List[UnresolvedItem]:
        """Get all unresolved items"""
        items = [item for item in self.unresolved_queue.values() if not item.resolved]
        # Sort by created_at descending
        return sorted(items, key=lambda x: x.created_at, reverse=True)
    
    def resolve_item(self, request: ResolveItemRequest, professor_id: str) -> UnresolvedItem:
        """Resolve an unresolved queue item"""
        if request.item_id not in self.unresolved_queue:
            raise ValueError(f"Item {request.item_id} not found")
        
        item = self.unresolved_queue[request.item_id]
        
        if request.action == "link" and request.canonical_answer_id:
            item.linked_canonical_id = request.canonical_answer_id
        elif request.action == "create" and request.new_answer:
            # Create new canonical answer
            canonical = self.create_canonical_answer(request.new_answer, professor_id)
            item.linked_canonical_id = canonical.answer_id
        
        item.resolved = True
        item.resolved_by = professor_id
        item.resolved_at = datetime.now()
        
        return item
    
    # Confusion Heatmap
    def log_confusion_signal(self, student_id: str, artifact: str, section: Optional[str],
                            question: str, signal_type: str):
        """Log a confusion signal (stuck, repeated question, etc.)"""
        signal = ConfusionSignal(
            signal_id=str(uuid.uuid4()),
            student_id=student_id,
            artifact=artifact,
            section=section,
            question=question,
            timestamp=datetime.now(),
            signal_type=signal_type
        )
        self.confusion_signals.append(signal)
    
    def get_confusion_heatmap(self, course_id: str, days: int = 7) -> List[ConfusionHeatmapEntry]:
        """Generate confusion heatmap for recent signals"""
        cutoff = datetime.now() - timedelta(days=days)
        recent_signals = [s for s in self.confusion_signals if s.timestamp >= cutoff]
        
        # Group by artifact + section
        grouped: Dict[tuple, List[ConfusionSignal]] = defaultdict(list)
        for signal in recent_signals:
            key = (signal.artifact, signal.section or "general")
            grouped[key].append(signal)
        
        # Create heatmap entries
        heatmap = []
        for (artifact, section), signals in grouped.items():
            unique_students = len(set(s.student_id for s in signals))
            example_questions = list(set(s.question for s in signals[:5]))  # Top 5 unique
            
            entry = ConfusionHeatmapEntry(
                artifact=artifact,
                section=section if section != "general" else None,
                confusion_count=len(signals),
                unique_students=unique_students,
                example_questions=example_questions,
                last_updated=max(s.timestamp for s in signals)
            )
            heatmap.append(entry)
        
        # Sort by confusion count descending
        return sorted(heatmap, key=lambda x: x.confusion_count, reverse=True)
    
    # Guardrail Settings
    def get_guardrail_settings(self, course_id: str) -> GuardrailSettings:
        """Get guardrail settings for a course"""
        if course_id not in self.guardrail_settings:
            # Return defaults
            return GuardrailSettings(
                course_id=course_id,
                updated_by="system",
                updated_at=datetime.now()
            )
        return self.guardrail_settings[course_id]
    
    def update_guardrail_settings(self, course_id: str, request: UpdateGuardrailRequest,
                                 professor_id: str) -> GuardrailSettings:
        """Update guardrail settings"""
        settings = self.get_guardrail_settings(course_id)
        
        if request.max_hints is not None:
            settings.max_hints = request.max_hints
        if request.show_thinking_path is not None:
            settings.show_thinking_path = request.show_thinking_path
        if request.graded_banner_text is not None:
            settings.graded_banner_text = request.graded_banner_text
        if request.assignment_rubrics is not None:
            settings.assignment_rubrics.update(request.assignment_rubrics)
        
        settings.updated_by = professor_id
        settings.updated_at = datetime.now()
        
        self.guardrail_settings[course_id] = settings
        return settings
    
    # Enhanced Semantic Clustering
    def get_semantic_clusters(self, course_id: str, similarity_threshold: float = 0.75, min_count: int = 2):
        """
        Get question clusters using semantic similarity (embeddings)
        Groups questions that are semantically similar, not just keyword-based
        """
        if not self.embedder or not self.question_logs:
            # Fallback to simple clustering
            return self.get_question_clusters(course_id, min_count)
        
        # Get all questions
        questions = [log["question"] for log in self.question_logs]
        
        if len(questions) < 2:
            return []
        
        # Generate embeddings
        embeddings = self.embedder.encode(questions)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Cluster using similarity threshold
        clusters_list = []
        assigned = set()
        
        for i in range(len(questions)):
            if i in assigned:
                continue
            
            # Find all similar questions
            similar_indices = []
            for j in range(len(questions)):
                if i != j and similarity_matrix[i][j] >= similarity_threshold:
                    similar_indices.append(j)
            
            if len(similar_indices) >= min_count - 1:  # Including the seed question
                # Create cluster
                cluster_questions = [questions[i]] + [questions[j] for j in similar_indices]
                assigned.add(i)
                assigned.update(similar_indices)
                
                # Get metadata from logs
                log_indices = [i] + similar_indices
                artifacts = [self.question_logs[idx].get("artifact") for idx in log_indices]
                sections = [self.question_logs[idx].get("section") for idx in log_indices]
                
                # Most common artifact/section
                artifact = max(set(filter(None, artifacts)), key=artifacts.count) if artifacts else None
                section = max(set(filter(None, sections)), key=sections.count) if sections else None
                
                cluster = QuestionCluster(
                    cluster_id=str(uuid.uuid4()),
                    representative_question=questions[i],  # First question as representative
                    similar_questions=cluster_questions,
                    count=len(cluster_questions),
                    artifact=artifact,
                    section=section,
                    canonical_answer_id=None,
                    created_at=datetime.now(),
                    last_seen=datetime.now()
                )
                clusters_list.append(cluster)
        
        return sorted(clusters_list, key=lambda x: x.count, reverse=True)
    
    def suggest_cluster_name(self, cluster: QuestionCluster) -> str:
        """
        Suggest a descriptive name for a cluster based on its questions
        """
        # Simple heuristic: extract common keywords
        questions = cluster.similar_questions
        
        # Check for common patterns
        if any("due" in q.lower() or "deadline" in q.lower() for q in questions):
            artifact = cluster.artifact or "Assignment"
            return f"{artifact} - Deadline Questions"
        elif any("policy" in q.lower() for q in questions):
            return f"{cluster.section or 'Course'} Policy Questions"
        elif any("help" in q.lower() or "stuck" in q.lower() for q in questions):
            return f"{cluster.artifact or cluster.section or 'Topic'} - Help Requests"
        else:
            return f"{cluster.artifact or cluster.section or 'General'} Questions"
    
    def find_canonical_answer(self, question: str, similarity_threshold: float = 0.75) -> Optional[CanonicalAnswer]:
        """
        Check if a student question matches any canonical answer
        Returns the canonical answer if found, None otherwise
        """
        if not self.embedder or not self.canonical_answers:
            return None
        
        # Get published canonical answers
        published_answers = [
            answer for answer in self.canonical_answers.values()
            if answer.published
        ]
        
        if not published_answers:
            return None
        
        # Generate embedding for the question
        question_embedding = self.embedder.encode([question])
        
        # Check each canonical answer's cluster
        for answer in published_answers:
            # Find the cluster this answer belongs to
            cluster_questions = []
            for cluster in self.clusters.values():
                if cluster.canonical_answer_id == answer.answer_id:
                    cluster_questions = cluster.similar_questions
                    break
            
            if not cluster_questions:
                continue
            
            # Generate embeddings for cluster questions
            cluster_embeddings = self.embedder.encode(cluster_questions)
            
            # Calculate similarity
            similarities = cosine_similarity(question_embedding, cluster_embeddings)[0]
            max_similarity = max(similarities)
            
            if max_similarity >= similarity_threshold:
                return answer
        
        return None
    
    def get_all_published_canonical_answers(self) -> List[CanonicalAnswer]:
        """Get all published canonical answers for FAQ page"""
        return [
            answer for answer in self.canonical_answers.values()
            if answer.published
        ]
