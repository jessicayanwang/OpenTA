"""
Behavioral Signal Tracker
Detects struggle patterns during assignment help and chat sessions
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum

class StruggleSignal(str, Enum):
    """Types of struggle signals"""
    MULTIPLE_HINTS = "multiple_hints"           # Asked for >2 hints on same problem
    LONG_DWELL = "long_dwell"                   # Spent >10 min without progress
    REPEATED_ERRORS = "repeated_errors"         # Same type of error multiple times
    COPY_PASTE = "copy_paste"                   # Excessive copy/paste behavior
    LOW_CONFIDENCE = "low_confidence"           # Student explicitly says "I don't know"
    RAPID_QUESTIONS = "rapid_questions"         # Many questions in short time
    OFF_TOPIC = "off_topic"                     # Questions indicate confusion about basics

@dataclass
class SessionActivity:
    """Tracks activity within a single session"""
    session_id: str
    student_id: str
    topic: str
    start_time: datetime
    
    # Behavioral metrics
    hint_requests: int = 0
    questions_asked: int = 0
    time_on_task_seconds: float = 0.0
    copy_paste_count: int = 0
    error_repeats: Dict[str, int] = field(default_factory=dict)
    
    # Signals detected
    signals_detected: List[StruggleSignal] = field(default_factory=list)
    intervention_offered: bool = False
    intervention_accepted: bool = False

@dataclass
class StudentBehaviorProfile:
    """Long-term behavioral profile for a student"""
    student_id: str
    
    # Historical patterns
    total_sessions: int = 0
    total_hints_used: int = 0
    average_session_length: float = 0.0  # minutes
    
    # Struggle patterns
    topics_with_struggles: Dict[str, int] = field(default_factory=dict)  # topic -> struggle_count
    recent_signals: List[tuple] = field(default_factory=list)  # (timestamp, signal, topic)
    
    # Learning style indicators
    hint_preference: float = 0.5  # 0=avoid hints, 1=relies on hints
    persistence: float = 0.5      # How long they stick with problems
    asks_for_help: float = 0.5    # Tendency to ask questions vs struggle alone

class BehavioralTracker:
    """
    Tracks behavioral signals to detect when students need intervention
    """
    
    def __init__(self):
        self.active_sessions: Dict[str, SessionActivity] = {}
        self.student_profiles: Dict[str, StudentBehaviorProfile] = {}
        
        # Thresholds for triggering interventions
        self.HINT_THRESHOLD = 3
        self.DWELL_THRESHOLD_MINUTES = 10
        self.ERROR_REPEAT_THRESHOLD = 2
        self.RAPID_QUESTION_WINDOW = 5  # minutes
        self.RAPID_QUESTION_COUNT = 5
    
    def start_session(self, session_id: str, student_id: str, topic: str) -> SessionActivity:
        """Start tracking a new session"""
        session = SessionActivity(
            session_id=session_id,
            student_id=student_id,
            topic=topic,
            start_time=datetime.now()
        )
        
        self.active_sessions[session_id] = session
        
        # Initialize student profile if needed
        if student_id not in self.student_profiles:
            self.student_profiles[student_id] = StudentBehaviorProfile(student_id=student_id)
        
        return session
    
    def log_hint_request(self, session_id: str, hint_type: str = "general"):
        """Log when student requests a hint"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.hint_requests += 1
        
        # Check for excessive hint usage
        if session.hint_requests >= self.HINT_THRESHOLD:
            if StruggleSignal.MULTIPLE_HINTS not in session.signals_detected:
                session.signals_detected.append(StruggleSignal.MULTIPLE_HINTS)
                self._record_signal(session, StruggleSignal.MULTIPLE_HINTS)
    
    def log_question(self, session_id: str, question: str):
        """Log when student asks a question"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.questions_asked += 1
        
        # Check for rapid-fire questions (confusion indicator)
        session_duration = (datetime.now() - session.start_time).total_seconds() / 60
        if session_duration < self.RAPID_QUESTION_WINDOW:
            if session.questions_asked >= self.RAPID_QUESTION_COUNT:
                if StruggleSignal.RAPID_QUESTIONS not in session.signals_detected:
                    session.signals_detected.append(StruggleSignal.RAPID_QUESTIONS)
                    self._record_signal(session, StruggleSignal.RAPID_QUESTIONS)
        
        # Check for low confidence language
        low_confidence_phrases = ["i don't know", "confused", "no idea", "lost", "don't understand"]
        if any(phrase in question.lower() for phrase in low_confidence_phrases):
            if StruggleSignal.LOW_CONFIDENCE not in session.signals_detected:
                session.signals_detected.append(StruggleSignal.LOW_CONFIDENCE)
                self._record_signal(session, StruggleSignal.LOW_CONFIDENCE)
    
    def log_error(self, session_id: str, error_type: str):
        """Log when student encounters an error"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        
        if error_type not in session.error_repeats:
            session.error_repeats[error_type] = 0
        session.error_repeats[error_type] += 1
        
        # Check for repeated errors
        if session.error_repeats[error_type] >= self.ERROR_REPEAT_THRESHOLD:
            if StruggleSignal.REPEATED_ERRORS not in session.signals_detected:
                session.signals_detected.append(StruggleSignal.REPEATED_ERRORS)
                self._record_signal(session, StruggleSignal.REPEATED_ERRORS)
    
    def log_copy_paste(self, session_id: str):
        """Log copy/paste activity"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.copy_paste_count += 1
        
        # Excessive copy/paste may indicate confusion or trial-and-error
        if session.copy_paste_count >= 5:
            if StruggleSignal.COPY_PASTE not in session.signals_detected:
                session.signals_detected.append(StruggleSignal.COPY_PASTE)
                self._record_signal(session, StruggleSignal.COPY_PASTE)
    
    def update_time_on_task(self, session_id: str):
        """Update time spent on current task"""
        if session_id not in self.active_sessions:
            return
        
        session = self.active_sessions[session_id]
        session.time_on_task_seconds = (datetime.now() - session.start_time).total_seconds()
        
        # Check for long dwell time without progress
        minutes_elapsed = session.time_on_task_seconds / 60
        if minutes_elapsed >= self.DWELL_THRESHOLD_MINUTES:
            # If they've been stuck for a while with minimal interaction
            if session.questions_asked == 0 or session.hint_requests == 0:
                if StruggleSignal.LONG_DWELL not in session.signals_detected:
                    session.signals_detected.append(StruggleSignal.LONG_DWELL)
                    self._record_signal(session, StruggleSignal.LONG_DWELL)
    
    def should_offer_intervention(self, session_id: str) -> Dict:
        """
        Determine if we should offer a concept check or other intervention
        Returns intervention recommendation
        """
        if session_id not in self.active_sessions:
            return {"offer": False}
        
        session = self.active_sessions[session_id]
        
        # Already offered intervention
        if session.intervention_offered:
            return {"offer": False}
        
        # Need at least 2 signals to trigger intervention
        if len(session.signals_detected) < 2:
            return {"offer": False}
        
        # Determine intervention type based on signals
        signals = session.signals_detected
        
        intervention = {
            "offer": True,
            "type": "concept_check",
            "reason": self._explain_signals(signals),
            "signals": [s.value for s in signals],
            "suggested_action": "Take a quick 2-question concept check to identify gaps"
        }
        
        # Mark as offered
        session.intervention_offered = True
        
        return intervention
    
    def record_intervention_response(self, session_id: str, accepted: bool):
        """Record whether student accepted the intervention"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].intervention_accepted = accepted
    
    def end_session(self, session_id: str) -> Dict:
        """
        End a session and update student profile
        Returns session summary
        """
        if session_id not in self.active_sessions:
            return {}
        
        session = self.active_sessions[session_id]
        profile = self.student_profiles[session.student_id]
        
        # Update profile statistics
        profile.total_sessions += 1
        profile.total_hints_used += session.hint_requests
        
        # Update average session length
        session_minutes = session.time_on_task_seconds / 60
        profile.average_session_length = (
            (profile.average_session_length * (profile.total_sessions - 1) + session_minutes) 
            / profile.total_sessions
        )
        
        # Update struggle topics
        if session.signals_detected:
            if session.topic not in profile.topics_with_struggles:
                profile.topics_with_struggles[session.topic] = 0
            profile.topics_with_struggles[session.topic] += len(session.signals_detected)
        
        # Update learning style indicators
        alpha = 0.2  # Learning rate
        
        # Hint preference
        hints_per_session = session.hint_requests / max(session.questions_asked, 1)
        profile.hint_preference = (1 - alpha) * profile.hint_preference + alpha * min(hints_per_session, 1.0)
        
        # Persistence
        persistence_score = min(session.time_on_task_seconds / 600, 1.0)  # 10 min = max persistence
        profile.persistence = (1 - alpha) * profile.persistence + alpha * persistence_score
        
        # Asks for help
        help_seeking = min(session.questions_asked / 5, 1.0)  # 5 questions = high help-seeking
        profile.asks_for_help = (1 - alpha) * profile.asks_for_help + alpha * help_seeking
        
        # Create summary
        summary = {
            "session_id": session_id,
            "duration_minutes": session_minutes,
            "hints_used": session.hint_requests,
            "questions_asked": session.questions_asked,
            "signals_detected": [s.value for s in session.signals_detected],
            "intervention_offered": session.intervention_offered,
            "intervention_accepted": session.intervention_accepted,
            "profile_update": {
                "hint_preference": profile.hint_preference,
                "persistence": profile.persistence,
                "help_seeking": profile.asks_for_help
            }
        }
        
        # Clean up
        del self.active_sessions[session_id]
        
        return summary
    
    def get_student_struggle_topics(self, student_id: str) -> List[tuple]:
        """Get topics where student has struggled, sorted by struggle frequency"""
        if student_id not in self.student_profiles:
            return []
        
        profile = self.student_profiles[student_id]
        
        # Sort topics by struggle count
        struggles = sorted(
            profile.topics_with_struggles.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        return struggles
    
    def _record_signal(self, session: SessionActivity, signal: StruggleSignal):
        """Record a signal in student's long-term profile"""
        profile = self.student_profiles[session.student_id]
        profile.recent_signals.append((datetime.now(), signal, session.topic))
        
        # Keep only last 50 signals
        if len(profile.recent_signals) > 50:
            profile.recent_signals = profile.recent_signals[-50:]
    
    def _explain_signals(self, signals: List[StruggleSignal]) -> str:
        """Generate human-readable explanation of signals"""
        explanations = {
            StruggleSignal.MULTIPLE_HINTS: "You've requested several hints",
            StruggleSignal.LONG_DWELL: "You've been working on this for a while",
            StruggleSignal.REPEATED_ERRORS: "You're encountering the same error repeatedly",
            StruggleSignal.COPY_PASTE: "There's a lot of trial-and-error happening",
            StruggleSignal.LOW_CONFIDENCE: "You mentioned feeling confused",
            StruggleSignal.RAPID_QUESTIONS: "You have several questions coming up quickly",
            StruggleSignal.OFF_TOPIC: "Some confusion about fundamental concepts"
        }
        
        parts = [explanations.get(s, str(s)) for s in signals[:3]]  # Top 3 signals
        
        if len(parts) == 1:
            return parts[0]
        elif len(parts) == 2:
            return f"{parts[0]} and {parts[1]}"
        else:
            return f"{', '.join(parts[:-1])}, and {parts[-1]}"
