"""
Exam Runway - 7-Day Exam Preparation System
Generates compressed study plans and daily gap checks when exam is approaching
"""
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from dataclasses import dataclass

from models import StudyTask, WeekPlan
from adaptive.spaced_repetition import SpacedRepetitionEngine

@dataclass
class DailyTarget:
    """Target for a single day in exam runway"""
    day_number: int  # 1-7 (7 = exam day)
    date: datetime
    focus_topics: List[str]
    time_blocks: List[StudyTask]
    gap_check_items: int  # Number of quiz items for evening gap check
    intensity: str  # "high", "medium", "low", "rest"

@dataclass
class ExamRunway:
    """7-day exam preparation plan"""
    exam_type: str  # "midterm" or "final"
    exam_date: datetime
    days_until_exam: int
    daily_targets: List[DailyTarget]
    priority_topics: List[str]  # Topics identified as weak
    total_hours_allocated: float

class ExamRunwayService:
    """
    Generates and manages 7-day exam preparation plans
    """
    
    def __init__(self, spaced_rep_engine: SpacedRepetitionEngine):
        self.spaced_rep_engine = spaced_rep_engine
    
    def generate_runway(
        self,
        student_id: str,
        exam_date: datetime,
        exam_type: str,  # "midterm" or "final"
        hours_per_day: float = 3.0,
        course_id: str = "cs50"
    ) -> ExamRunway:
        """
        Generate a 7-day exam preparation plan
        """
        # Make both datetimes timezone-aware for comparison
        now = datetime.now(timezone.utc)
        if exam_date.tzinfo is None:
            exam_date = exam_date.replace(tzinfo=timezone.utc)
        
        days_until = (exam_date - now).days
        
        if days_until > 7:
            # Generate preview (what plan will look like when closer)
            days_until = 7
            exam_date = now + timedelta(days=7)
        
        # Identify weak topics from spaced repetition data
        weak_topics = self.spaced_rep_engine.get_weak_topics(student_id, threshold=0.7)
        priority_topics = [topic for topic, score, conf in weak_topics[:5]]  # Top 5 weak topics
        
        # If no weak topics identified, use comprehensive review
        if not priority_topics:
            if exam_type == "midterm":
                priority_topics = ["C Basics", "Arrays", "Algorithms", "Memory"]
            else:  # final
                priority_topics = ["C Programming", "Data Structures", "Python", "SQL", "Web Dev"]
        
        # Generate daily targets for each day
        daily_targets = []
        for day in range(1, min(days_until, 7) + 1):
            target_date = now + timedelta(days=day)
            target = self._generate_daily_target(
                day_number=day,
                target_date=target_date,
                days_until_exam=days_until,
                hours_available=hours_per_day,
                priority_topics=priority_topics,
                exam_type=exam_type
            )
            daily_targets.append(target)
        
        return ExamRunway(
            exam_type=exam_type,
            exam_date=exam_date,
            days_until_exam=days_until,
            daily_targets=daily_targets,
            priority_topics=priority_topics,
            total_hours_allocated=hours_per_day * len(daily_targets)
        )
    
    def _generate_daily_target(
        self,
        day_number: int,
        target_date: datetime,
        days_until_exam: int,
        hours_available: float,
        priority_topics: List[str],
        exam_type: str
    ) -> DailyTarget:
        """Generate study targets for a single day"""
        
        # Day-specific intensity and focus
        if day_number == 1:
            # Day 1: Assessment and planning
            intensity = "medium"
            focus = priority_topics[:2] if priority_topics else ["Review fundamentals"]
            time_blocks = [
                StudyTask(
                    day="Morning",
                    focus=f"Diagnostic review: {', '.join(focus)}",
                    duration_hours=hours_available * 0.4
                ),
                StudyTask(
                    day="Afternoon",
                    focus="Practice problems on weak areas",
                    duration_hours=hours_available * 0.4
                ),
                StudyTask(
                    day="Evening",
                    focus="Gap check quiz (5 items)",
                    duration_hours=hours_available * 0.2
                )
            ]
            gap_check_count = 5
        
        elif day_number <= 3:
            # Days 2-3: Intensive review of weak topics
            intensity = "high"
            topic_idx = (day_number - 2) % len(priority_topics) if priority_topics else 0
            focus = [priority_topics[topic_idx]] if priority_topics else ["Core concepts"]
            
            time_blocks = [
                StudyTask(
                    day="Morning",
                    focus=f"Deep dive: {focus[0]}",
                    duration_hours=hours_available * 0.5
                ),
                StudyTask(
                    day="Afternoon",
                    focus="Practice problems and worked examples",
                    duration_hours=hours_available * 0.3
                ),
                StudyTask(
                    day="Evening",
                    focus="Gap check + review mistakes",
                    duration_hours=hours_available * 0.2
                )
            ]
            gap_check_count = 5
        
        elif day_number == 4:
            # Day 4: Mock exam
            intensity = "high"
            focus = ["Mock exam", "Comprehensive review"]
            time_blocks = [
                StudyTask(
                    day="Morning",
                    focus="20-minute timed mock exam",
                    duration_hours=hours_available * 0.3
                ),
                StudyTask(
                    day="Afternoon",
                    focus="Review mock exam errors in detail",
                    duration_hours=hours_available * 0.5
                ),
                StudyTask(
                    day="Evening",
                    focus="Targeted practice on missed topics",
                    duration_hours=hours_available * 0.2
                )
            ]
            gap_check_count = 3
        
        elif day_number <= 6:
            # Days 5-6: Targeted weak areas from mock
            intensity = "medium"
            focus = ["High-yield topics", "Review challenging problems"]
            time_blocks = [
                StudyTask(
                    day="Morning",
                    focus="Review must-know concepts",
                    duration_hours=hours_available * 0.4
                ),
                StudyTask(
                    day="Afternoon",
                    focus="Practice recent problem set questions",
                    duration_hours=hours_available * 0.4
                ),
                StudyTask(
                    day="Evening",
                    focus="Light gap check",
                    duration_hours=hours_available * 0.2
                )
            ]
            gap_check_count = 3
        
        else:
            # Day 7: Light review and rest
            intensity = "low"
            focus = ["Quick review", "Mental preparation"]
            time_blocks = [
                StudyTask(
                    day="Morning",
                    focus="Skim through notes and flashcards",
                    duration_hours=hours_available * 0.4
                ),
                StudyTask(
                    day="Afternoon",
                    focus="One or two easy practice problems",
                    duration_hours=hours_available * 0.2
                ),
                StudyTask(
                    day="Evening",
                    focus="Rest and get good sleep!",
                    duration_hours=hours_available * 0.4
                )
            ]
            gap_check_count = 0
        
        return DailyTarget(
            day_number=day_number,
            date=target_date,
            focus_topics=focus,
            time_blocks=time_blocks,
            gap_check_items=gap_check_count,
            intensity=intensity
        )
    
    def adjust_runway_after_gap_check(
        self,
        runway: ExamRunway,
        day_number: int,
        weak_topics_found: List[str]
    ) -> ExamRunway:
        """
        Adjust remaining days based on gap check results
        Inserts prerequisite refreshers and high-yield problems
        """
        # Find the day to adjust (next day)
        next_day_idx = day_number  # 0-indexed
        
        if next_day_idx >= len(runway.daily_targets):
            return runway  # No more days to adjust
        
        # Update next day's focus to prioritize newly identified weak topics
        next_target = runway.daily_targets[next_day_idx]
        
        # Prepend weak topics to focus
        next_target.focus_topics = weak_topics_found + next_target.focus_topics
        
        # Update time blocks to emphasize weak topics
        if next_target.time_blocks:
            next_target.time_blocks[0] = StudyTask(
                day=next_target.time_blocks[0].day,
                focus=f"Prerequisite refresher: {', '.join(weak_topics_found[:2])}",
                duration_hours=next_target.time_blocks[0].duration_hours
            )
        
        return runway
    
    def get_daily_gap_check_questions(
        self,
        student_id: str,
        runway: ExamRunway,
        day_number: int
    ) -> List[Dict]:
        """
        Get gap check questions for a specific day
        Returns questions focused on that day's topics
        """
        if day_number <= 0 or day_number > len(runway.daily_targets):
            return []
        
        target = runway.daily_targets[day_number - 1]
        
        if target.gap_check_items == 0:
            return []
        
        # Get questions for the day's focus topics
        questions = []
        topics_covered = target.focus_topics[:2]  # Focus on top 2 topics
        
        for topic in topics_covered:
            # Get due cards for this topic
            due_cards = self.spaced_rep_engine.get_due_cards(
                student_id, 
                topic=topic,
                limit=target.gap_check_items // len(topics_covered) if topics_covered else target.gap_check_items
            )
            
            for card in due_cards:
                questions.append({
                    "question_id": card.card_id,
                    "topic": topic,
                    "question": card.question_text,
                    "options": [card.correct_answer] + card.distractors,
                    "source": f"Gap check - Day {day_number}"
                })
        
        return questions[:target.gap_check_items]
    
    def generate_mock_exam(self, student_id: str, exam_type: str) -> List[Dict]:
        """
        Generate a 20-minute mock exam
        ~10-15 questions covering key topics
        """
        if exam_type == "midterm":
            topics = ["C Basics", "Arrays", "Algorithms", "Memory"]
            num_questions = 12
        else:  # final
            topics = ["C Programming", "Data Structures", "Python", "SQL", "Web"]
            num_questions = 15
        
        questions = []
        questions_per_topic = num_questions // len(topics)
        
        for topic in topics:
            # Get mix of due cards and new cards
            due = self.spaced_rep_engine.get_due_cards(student_id, topic, limit=questions_per_topic // 2)
            new = self.spaced_rep_engine.get_new_cards(student_id, topic, limit=questions_per_topic // 2)
            
            topic_questions = due + new
            
            for card in topic_questions[:questions_per_topic]:
                questions.append({
                    "question_id": card.card_id,
                    "topic": topic,
                    "question": card.question_text,
                    "options": [card.correct_answer] + card.distractors,
                    "difficulty": card.difficulty
                })
        
        return questions[:num_questions]
