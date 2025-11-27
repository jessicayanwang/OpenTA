"""
Pop Quiz Service
Generates quiz items strictly from course content (syllabus + notes)
All questions are content-scoped and traceable to source documents
"""
from typing import List, Dict, Optional
from datetime import datetime
import re
import os
import json
from dataclasses import dataclass
from openai import OpenAI
from document_store import DocumentStore, DocumentChunk
from retrieval import HybridRetriever
from adaptive.spaced_repetition import SpacedRepetitionEngine, ReviewCard

@dataclass
class PopQuizItem:
    """A single pop quiz question"""
    question_id: str
    topic: str
    subtopic: str
    question: str
    options: List[str]
    correct_index: int
    difficulty: float
    source_citation: str  # Which document/section this came from
    explanation: str      # Why this answer is correct

class PopQuizService:
    """
    Generates personalized pop quiz items from course materials
    All questions are content-scoped and traceable to source documents
    """
    
    def __init__(
        self, 
        document_store: DocumentStore,
        retriever: HybridRetriever,
        spaced_rep_engine: SpacedRepetitionEngine
    ):
        self.document_store = document_store
        self.retriever = retriever
        self.spaced_rep_engine = spaced_rep_engine
        
        # Initialize OpenAI client if API key available
        self.use_openai = bool(os.getenv("OPENAI_API_KEY"))
        if self.use_openai:
            self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            print("  ✓ OpenAI enabled for on-demand quiz generation")
        else:
            self.openai_client = None
            print("  ⚠ OpenAI not configured - using simple patterns")
        
        # Cache for generated questions (to avoid regenerating)
        self.question_cache: Dict[str, PopQuizItem] = {}
        print("  ✓ Pop Quiz Service ready (on-demand generation)")
    
    def _determine_quiz_scope(self, student_id: str, quiz_type: str = "daily") -> Dict:
        """
        Determine what material to quiz on based on:
        1. Student's weak topics (from mastery tracking)
        2. Spaced repetition schedule (what's due for review)
        3. Current course progress (what's been taught)
        4. Request type (daily vs exam prep)
        """
        scope = {
            "weak_topics": [],
            "due_for_review": [],
            "recent_topics": [],
            "material_cutoff": None
        }
        
        # 1. Get weak topics from mastery
        if student_id in self.spaced_rep_engine.student_mastery:
            for topic, mastery in self.spaced_rep_engine.student_mastery[student_id].items():
                if mastery.mastery_score < 0.6:
                    scope["weak_topics"].append(topic)
        
        # 2. Get topics due for review (forgetting curve)
        # Check cards within each topic's mastery
        if student_id in self.spaced_rep_engine.student_mastery:
            now = datetime.now()
            for topic, mastery in self.spaced_rep_engine.student_mastery[student_id].items():
                for card in mastery.cards:
                    if card.next_review and card.next_review <= now:
                        if topic not in scope["due_for_review"]:
                            scope["due_for_review"].append(topic)
                        break
        
        # 3. Determine material scope based on quiz type
        if quiz_type == "daily":
            # Daily: Last week's material + weak topics
            scope["material_cutoff"] = "last_week"
        elif quiz_type == "exam":
            # Exam: All exam-relevant material
            scope["material_cutoff"] = "exam_topics"
        
        return scope
    
    def _group_chunks_by_topic(self) -> Dict[str, List[DocumentChunk]]:
        """Group document chunks by topic based on source and section"""
        topics = {}
        
        for chunk in self.document_store.chunks:
            # Derive topic from source file
            topic = self._derive_topic(chunk.source, chunk.section)
            
            if topic not in topics:
                topics[topic] = []
            topics[topic].append(chunk)
        
        return topics
    
    def _derive_topic(self, source: str, section: str) -> str:
        """Derive topic name from source file and section"""
        # Map file names to topics
        if "note0" in source or "scratch" in section.lower():
            return "Scratch & Computational Thinking"
        elif "note1" in source or section.lower().startswith("week 1"):
            return "C Programming Basics"
        elif "note2" in source:
            return "Arrays and Strings"
        elif "note3" in source:
            return "Algorithms"
        elif "note4" in source:
            return "Memory Management"
        elif "note5" in source:
            return "Data Structures"
        elif "note6" in source:
            return "Python"
        elif "note7" in source:
            return "SQL and Databases"
        elif "note8" in source:
            return "Web Development"
        elif "syllabus" in source:
            return "Course Policies"
        elif "assignment" in source:
            return "Problem Sets"
        else:
            return "General CS50"
    
    def _generate_questions_with_openai(self, chunk: DocumentChunk, topic: str) -> List[PopQuizItem]:
        """
        Use OpenAI to generate high-quality quiz questions from content
        """
        if not self.use_openai:
            return []
        
        try:
            prompt = f"""Based on the following course content, generate 2 multiple-choice quiz questions.

Content:
{chunk.text[:800]}

Generate questions that:
1. Test understanding of key concepts (not memorization)
2. Have 4 plausible options (not obvious wrong answers)
3. Are clear and unambiguous
4. Focus on practical application

Return ONLY a JSON array with this exact format:
[
  {{
    "question": "...",
    "options": ["...", "...", "...", "..."],
    "correct_index": 0,
    "explanation": "..."
  }}
]"""

            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a CS50 teaching assistant creating quiz questions. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=800
            )
            
            content = response.choices[0].message.content.strip()
            # Remove markdown code blocks if present
            if content.startswith("```"):
                content = content.split("```")[1]
                if content.startswith("json"):
                    content = content[4:]
            
            questions_data = json.loads(content)
            
            # Convert to PopQuizItem objects
            questions = []
            for i, q_data in enumerate(questions_data[:2]):  # Max 2 per chunk
                question_id = f"{chunk.source}_{chunk.section}_ai_{i}"
                questions.append(PopQuizItem(
                    question_id=question_id,
                    topic=topic,
                    subtopic=chunk.section,
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_index=q_data["correct_index"],
                    difficulty=0.6,
                    source_citation=f"{chunk.source} - {chunk.section}",
                    explanation=q_data.get("explanation", "Refer to course materials")
                ))
            
            return questions
            
        except Exception as e:
            print(f"  ⚠ OpenAI question generation failed: {str(e)}")
            return []
    
    def _generate_questions_from_chunk(self, chunk: DocumentChunk, topic: str) -> List[PopQuizItem]:
        """
        Generate quiz questions from a document chunk
        Tries OpenAI first, falls back to pattern matching
        """
        # Try OpenAI first if available
        if self.use_openai:
            questions = self._generate_questions_with_openai(chunk, topic)
            if questions:
                return questions
        
        # Fallback to pattern matching if OpenAI not available or failed
        questions = []
        text = chunk.text.lower()
        
        # Pattern 1: Definition questions (look for "is a", "is the")
        def_pattern = r'(\w+(?:\s+\w+){0,2})\s+is\s+(?:a|an|the)\s+([^.]+)'
        definitions = re.findall(def_pattern, text)
        
        for term, definition in definitions[:2]:  # Limit to 2 per chunk
            if len(definition) > 20:  # Meaningful definition
                question_id = f"{chunk.source}_{chunk.section}_{len(questions)}"
                
                # Create a "What is X?" question
                questions.append(PopQuizItem(
                    question_id=question_id,
                    topic=topic,
                    subtopic=chunk.section,
                    question=f"What is {term.strip()}?",
                    options=[
                        definition.strip()[:100],
                        "A type of loop structure",
                        "A memory allocation method",
                        "A sorting algorithm"
                    ],
                    correct_index=0,
                    difficulty=0.5,
                    source_citation=f"{chunk.source} - {chunk.section}",
                    explanation=f"According to the course materials: {definition.strip()[:150]}"
                ))
        
        # Pattern 2: Procedural questions (look for steps, "first", "then")
        if "first" in text and "then" in text:
            question_id = f"{chunk.source}_{chunk.section}_proc_{len(questions)}"
            
            questions.append(PopQuizItem(
                question_id=question_id,
                topic=topic,
                subtopic=chunk.section,
                question=f"According to the course materials on {chunk.section}, what is the correct sequence?",
                options=[
                    "Follow the steps as described in the section",
                    "Skip directly to the last step",
                    "Start from the middle",
                    "Reverse the order"
                ],
                correct_index=0,
                difficulty=0.6,
                source_citation=f"{chunk.source} - {chunk.section}",
                explanation=f"The section describes the proper sequence"
            ))
        
        # Pattern 3: Factual recall (numbers, dates, specific terms)
        numbers = re.findall(r'\b\d+\b', text)
        if numbers and len(chunk.text) > 50:
            question_id = f"{chunk.source}_{chunk.section}_fact_{len(questions)}"
            
            questions.append(PopQuizItem(
                question_id=question_id,
                topic=topic,
                subtopic=chunk.section,
                question=f"Which statement is true about {chunk.section}?",
                options=[
                    chunk.text[:80] + "...",
                    "This is not covered in the course",
                    "The opposite is true",
                    "This only applies in rare cases"
                ],
                correct_index=0,
                difficulty=0.4,
                source_citation=f"{chunk.source} - {chunk.section}",
                explanation=f"This is stated in {chunk.source}"
            ))
        
        return questions
    
    def get_daily_quiz(
        self, 
        student_id: str, 
        num_items: int = 3
    ) -> List[PopQuizItem]:
        """
        ADAPTIVE: Generate quiz on-demand based on:
        1. Weak topics (what student got wrong)
        2. Spaced repetition schedule (forgetting curve)
        3. Recent course material (what's been taught)
        """
        quiz_items = []
        
        # STEP 1: Determine scope (multi-agent: context analyzer)
        scope = self._determine_quiz_scope(student_id, quiz_type="daily")
        
        # STEP 2: Prioritize topics to quiz
        topics_to_quiz = []
        
        # Priority 1: Topics due for review (forgetting curve)
        topics_to_quiz.extend(list(set(scope["due_for_review"]))[:2])
        
        # Priority 2: Weak topics (mastery < 60%)
        if len(topics_to_quiz) < num_items:
            topics_to_quiz.extend([t for t in scope["weak_topics"] if t not in topics_to_quiz][:1])
        
        # Priority 3: Fill with general review topics
        if len(topics_to_quiz) < num_items:
            all_topics = list(self.spaced_rep_engine.student_mastery.get(student_id, {}).keys())
            for topic in all_topics:
                if topic not in topics_to_quiz:
                    topics_to_quiz.append(topic)
                    if len(topics_to_quiz) >= num_items:
                        break
        
        # If no topics yet (new student), use general topics
        if not topics_to_quiz:
            topics_to_quiz = ["C Programming Basics", "Algorithms", "Memory"]
        
        # STEP 3: Generate questions ON-DEMAND for each topic
        for topic in topics_to_quiz[:num_items]:
            # Use retriever to find relevant chunks for this topic
            query = f"{topic} concepts and examples"
            chunks = self.retriever.retrieve(query, top_k=1)
            
            if chunks:
                chunk = chunks[0][0]  # Get top chunk
                # Generate question on-demand
                questions = self._generate_questions_from_chunk(chunk, topic)
                if questions:
                    question = questions[0]
                    quiz_items.append(question)
                    # Cache for later submission
                    self.question_cache[question.question_id] = question
        
        return quiz_items[:num_items]
    
    def get_concept_check(
        self, 
        student_id: str, 
        topic: str,
        num_items: int = 2
    ) -> List[PopQuizItem]:
        """
        ADAPTIVE: Generate concept check on-demand for struggling students
        Used during assignment help when behavioral signals detected
        """
        quiz_items = []
        
        # Use retriever to find easiest/foundational chunks for this topic
        query = f"{topic} introduction basics fundamentals"
        chunks = self.retriever.retrieve(query, top_k=2)
        
        for chunk, _ in chunks[:num_items]:
            questions = self._generate_questions_from_chunk(chunk, topic)
            if questions:
                question = questions[0]
                quiz_items.append(question)
                # Cache for later submission
                self.question_cache[question.question_id] = question
        
        return quiz_items[:num_items]
    
    def get_exam_prep_questions(
        self,
        student_id: str,
        exam_topics: List[str],
        num_items: int = 10
    ) -> List[PopQuizItem]:
        """
        ADAPTIVE: Generate exam prep questions based on exam scope
        Multi-agent approach:
        1. Determine exam material cutoff
        2. Identify weak topics within exam scope
        3. Generate harder questions from exam-relevant chunks
        """
        quiz_items = []
        
        # Get weak topics within exam scope
        weak_in_scope = []
        if student_id in self.spaced_rep_engine.student_mastery:
            for topic, mastery in self.spaced_rep_engine.student_mastery[student_id].items():
                if topic in exam_topics and mastery.mastery_score < 0.7:
                    weak_in_scope.append((topic, mastery.mastery_score))
        
        # Sort by weakness
        weak_in_scope.sort(key=lambda x: x[1])
        
        # Prioritize questions from weak exam topics
        topics_to_quiz = [t for t, _ in weak_in_scope] + exam_topics
        
        for topic in topics_to_quiz[:num_items]:
            query = f"{topic} advanced concepts practice problems"
            chunks = self.retriever.retrieve(query, top_k=1)
            
            if chunks:
                chunk = chunks[0][0]
                questions = self._generate_questions_from_chunk(chunk, topic)
                if questions:
                    question = questions[0]
                    quiz_items.append(question)
                    # Cache for later submission
                    self.question_cache[question.question_id] = question
                    if len(quiz_items) >= num_items:
                        break
        
        return quiz_items[:num_items]
    
    def submit_answer(
        self,
        student_id: str,
        quiz_item: PopQuizItem,
        selected_index: int,
        response_time_seconds: float
    ) -> Dict:
        """
        Submit an answer to a quiz item and update spaced repetition
        """
        is_correct = (selected_index == quiz_item.correct_index)
        
        # Convert to review card if not already tracked
        card = self._quiz_item_to_card(quiz_item)
        
        # Check if card exists in student's deck
        student_mastery = self.spaced_rep_engine.get_or_create_mastery(
            student_id, 
            quiz_item.topic
        )
        
        existing_card = None
        for c in student_mastery.cards:
            if c.card_id == card.card_id:
                existing_card = c
                break
        
        if not existing_card:
            # New card, add it
            self.spaced_rep_engine.add_card(student_id, card)
        
        # Determine review result
        if not is_correct:
            result = "forgot"
        elif response_time_seconds < 5:
            result = "easy"
        elif response_time_seconds < 15:
            result = "good"
        else:
            result = "hard"
        
        # Record the review
        from adaptive.spaced_repetition import ReviewResult
        updated_card = self.spaced_rep_engine.record_review(
            student_id,
            card.card_id,
            ReviewResult(result),
            response_time_seconds
        )
        
        # Return result with next review time
        return {
            "correct": is_correct,
            "correct_answer": quiz_item.options[quiz_item.correct_index],
            "explanation": quiz_item.explanation,
            "next_review": updated_card.next_review.isoformat() if updated_card.next_review else None,
            "mastery_update": {
                "topic": quiz_item.topic,
                "new_mastery": student_mastery.mastery_score,
                "confidence": student_mastery.confidence
            }
        }
    
    def _card_to_quiz_item(self, card: ReviewCard) -> PopQuizItem:
        """Convert a review card to a pop quiz item"""
        return PopQuizItem(
            question_id=card.card_id,
            topic=card.topic,
            subtopic=card.subtopic,
            question=card.question_text,
            options=[card.correct_answer] + card.distractors,
            correct_index=0,  # Correct answer is always first (will be shuffled in frontend)
            difficulty=card.difficulty,
            source_citation=card.content_source,
            explanation=f"This is covered in {card.content_source}"
        )
    
    def _quiz_item_to_card(self, item: PopQuizItem) -> ReviewCard:
        """Convert a pop quiz item to a review card"""
        return ReviewCard(
            card_id=item.question_id,
            topic=item.topic,
            subtopic=item.subtopic,
            difficulty=item.difficulty,
            content_source=item.source_citation,
            question_text=item.question,
            correct_answer=item.options[item.correct_index],
            distractors=[opt for i, opt in enumerate(item.options) if i != item.correct_index]
        )
