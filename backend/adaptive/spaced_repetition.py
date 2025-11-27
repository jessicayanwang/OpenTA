"""
Spaced Repetition Engine
Implements forgetting curve and optimal review scheduling (similar to SM-2/Anki algorithm)
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class ReviewResult(str, Enum):
    """Result of a review attempt"""
    FORGOT = "forgot"           # 0-1: Complete failure
    HARD = "hard"               # 2: Difficult to recall
    GOOD = "good"               # 3: Correct with effort
    EASY = "easy"               # 4: Perfect recall

@dataclass
class ReviewCard:
    """A single item to review (question, concept, problem)"""
    card_id: str
    topic: str
    subtopic: str
    difficulty: float           # 0.0-1.0 (from easy to hard)
    content_source: str         # e.g., "cs50_note3.txt", "cs50_syllabus.txt"
    question_text: str
    correct_answer: str
    distractors: List[str]
    
    # Spaced repetition state
    ease_factor: float = 2.5    # How "easy" this card is for the student
    interval_days: float = 1.0  # Days until next review
    repetitions: int = 0        # Number of successful reviews
    last_reviewed: Optional[datetime] = None
    next_review: Optional[datetime] = None
    
    # Performance tracking
    total_reviews: int = 0
    correct_count: int = 0
    average_response_time: float = 0.0  # seconds

@dataclass
class StudentMastery:
    """Tracks student's mastery of a topic"""
    student_id: str
    topic: str
    
    # Mastery estimation (0.0-1.0)
    mastery_score: float = 0.5  # Start at 50% (unknown)
    confidence: float = 0.1     # How certain we are (0-1)
    
    # Performance history
    attempts: int = 0
    correct: int = 0
    streak: int = 0             # Current correct streak
    
    # Spaced repetition cards for this topic
    cards: List[ReviewCard] = field(default_factory=list)
    
    # Last activity
    last_practiced: Optional[datetime] = None
    next_recommended_review: Optional[datetime] = None

class SpacedRepetitionEngine:
    """
    Manages spaced repetition scheduling using modified SM-2 algorithm
    """
    
    def __init__(self):
        self.student_mastery: Dict[str, Dict[str, StudentMastery]] = {}  # student_id -> topic -> mastery
        
    def get_or_create_mastery(self, student_id: str, topic: str) -> StudentMastery:
        """Get or create mastery tracking for a student-topic pair"""
        if student_id not in self.student_mastery:
            self.student_mastery[student_id] = {}
        
        if topic not in self.student_mastery[student_id]:
            self.student_mastery[student_id][topic] = StudentMastery(
                student_id=student_id,
                topic=topic
            )
        
        return self.student_mastery[student_id][topic]
    
    def add_card(self, student_id: str, card: ReviewCard):
        """Add a review card to a student's deck"""
        mastery = self.get_or_create_mastery(student_id, card.topic)
        
        # Initialize first review for tomorrow
        if card.next_review is None:
            card.next_review = datetime.now() + timedelta(days=1)
        
        mastery.cards.append(card)
    
    def record_review(self, student_id: str, card_id: str, result: ReviewResult, response_time_seconds: float) -> ReviewCard:
        """
        Record a review result and update card scheduling using SM-2 algorithm
        
        SM-2 Algorithm:
        - EF (Ease Factor) determines how quickly intervals grow
        - Intervals grow exponentially for successful reviews
        - Failed reviews reset to day 1
        """
        card = self._find_card(student_id, card_id)
        if not card:
            raise ValueError(f"Card {card_id} not found for student {student_id}")
        
        mastery = self.get_or_create_mastery(student_id, card.topic)
        
        # Update card statistics
        card.total_reviews += 1
        card.last_reviewed = datetime.now()
        
        # Update average response time (exponential moving average)
        alpha = 0.3
        card.average_response_time = (
            alpha * response_time_seconds + (1 - alpha) * card.average_response_time
        )
        
        # SM-2 Algorithm logic
        if result == ReviewResult.FORGOT:
            # Failed: reset to beginning
            card.repetitions = 0
            card.interval_days = 1.0
            card.ease_factor = max(1.3, card.ease_factor - 0.2)  # Make harder
            mastery.streak = 0
        else:
            # Successful review
            card.correct_count += 1
            mastery.correct += 1
            mastery.streak += 1
            
            if result == ReviewResult.HARD:
                card.ease_factor = max(1.3, card.ease_factor - 0.15)
                quality = 2
            elif result == ReviewResult.GOOD:
                quality = 3
            elif result == ReviewResult.EASY:
                card.ease_factor = min(2.5, card.ease_factor + 0.1)
                quality = 4
            else:
                quality = 3
            
            # Calculate new interval based on SM-2
            if card.repetitions == 0:
                card.interval_days = 1
            elif card.repetitions == 1:
                card.interval_days = 6
            else:
                card.interval_days = card.interval_days * card.ease_factor
            
            card.repetitions += 1
        
        # Schedule next review
        card.next_review = datetime.now() + timedelta(days=card.interval_days)
        
        # Update mastery tracking
        mastery.attempts += 1
        mastery.last_practiced = datetime.now()
        self._update_mastery_score(mastery)
        
        return card
    
    def get_due_cards(self, student_id: str, topic: Optional[str] = None, limit: int = 5) -> List[ReviewCard]:
        """
        Get cards that are due for review now
        Returns cards sorted by urgency (overdue first)
        """
        if student_id not in self.student_mastery:
            return []
        
        now = datetime.now()
        due_cards = []
        
        topics = [topic] if topic else self.student_mastery[student_id].keys()
        
        for t in topics:
            mastery = self.student_mastery[student_id][t]
            for card in mastery.cards:
                if card.next_review and card.next_review <= now:
                    # Calculate how overdue (for sorting)
                    overdue_hours = (now - card.next_review).total_seconds() / 3600
                    due_cards.append((overdue_hours, card))
        
        # Sort by most overdue first
        due_cards.sort(key=lambda x: -x[0])
        
        return [card for _, card in due_cards[:limit]]
    
    def get_new_cards(self, student_id: str, topic: str, limit: int = 3) -> List[ReviewCard]:
        """Get new (never reviewed) cards for a topic"""
        mastery = self.get_or_create_mastery(student_id, topic)
        
        new_cards = [
            card for card in mastery.cards 
            if card.total_reviews == 0
        ]
        
        # Sort by difficulty (easier first for new learners)
        new_cards.sort(key=lambda c: c.difficulty)
        
        return new_cards[:limit]
    
    def get_review_schedule(self, student_id: str, days_ahead: int = 7) -> Dict[str, List[ReviewCard]]:
        """
        Get upcoming review schedule for next N days
        Returns: {date_str: [cards due that day]}
        """
        if student_id not in self.student_mastery:
            return {}
        
        schedule = {}
        now = datetime.now()
        
        for topic, mastery in self.student_mastery[student_id].items():
            for card in mastery.cards:
                if card.next_review:
                    days_until = (card.next_review - now).days
                    if 0 <= days_until <= days_ahead:
                        date_key = card.next_review.strftime("%Y-%m-%d")
                        if date_key not in schedule:
                            schedule[date_key] = []
                        schedule[date_key].append(card)
        
        return schedule
    
    def _update_mastery_score(self, mastery: StudentMastery):
        """
        Update mastery score using Bayesian-inspired approach
        Mastery = f(success_rate, streak, recency)
        """
        if mastery.attempts == 0:
            return
        
        # Base success rate
        success_rate = mastery.correct / mastery.attempts
        
        # Streak bonus (up to +0.2)
        streak_bonus = min(0.2, mastery.streak * 0.02)
        
        # Recency penalty (decay if not practiced recently)
        if mastery.last_practiced:
            days_since = (datetime.now() - mastery.last_practiced).days
            recency_penalty = min(0.3, days_since * 0.01)
        else:
            recency_penalty = 0
        
        # Calculate new mastery (bounded 0-1)
        raw_score = success_rate + streak_bonus - recency_penalty
        mastery.mastery_score = max(0.0, min(1.0, raw_score))
        
        # Confidence grows with more attempts
        mastery.confidence = min(0.9, 0.1 + (mastery.attempts * 0.05))
    
    def _find_card(self, student_id: str, card_id: str) -> Optional[ReviewCard]:
        """Find a card by ID"""
        if student_id not in self.student_mastery:
            return None
        
        for topic, mastery in self.student_mastery[student_id].items():
            for card in mastery.cards:
                if card.card_id == card_id:
                    return card
        
        return None
    
    def get_weak_topics(self, student_id: str, threshold: float = 0.6) -> List[tuple]:
        """
        Get topics where student is struggling (mastery < threshold)
        Returns: [(topic, mastery_score, confidence), ...]
        """
        if student_id not in self.student_mastery:
            return []
        
        weak_topics = []
        for topic, mastery in self.student_mastery[student_id].items():
            if mastery.mastery_score < threshold and mastery.attempts >= 3:
                weak_topics.append((topic, mastery.mastery_score, mastery.confidence))
        
        # Sort by lowest mastery first
        weak_topics.sort(key=lambda x: x[1])
        
        return weak_topics
