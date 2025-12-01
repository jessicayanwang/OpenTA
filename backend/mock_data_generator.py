"""
Mock Data Generator for Professor Console Demo
Generates realistic student questions, interactions, and analytics
"""
import random
from datetime import datetime, timedelta
from professor_service import ProfessorService

class MockDataGenerator:
    """Generate realistic mock data for demo purposes"""
    
    def __init__(self, professor_service: ProfessorService):
        self.service = professor_service
        
        # Student personas
        self.students = [
            {"id": "student_001", "name": "Sarah Chen", "level": "struggling"},
            {"id": "student_002", "name": "Mike Johnson", "level": "average"},
            {"id": "student_003", "name": "Emma Davis", "level": "thriving"},
            {"id": "student_004", "name": "Alex Kim", "level": "struggling"},
            {"id": "student_005", "name": "Jordan Lee", "level": "average"},
            {"id": "student_006", "name": "Taylor Brown", "level": "silent"},
            {"id": "student_007", "name": "Casey Martinez", "level": "thriving"},
            {"id": "student_008", "name": "Morgan Wilson", "level": "average"},
        ]
        
        # Question templates by topic
        self.question_templates = {
            "deadlines": [
                "When is Problem Set {} due?",
                "What's the deadline for Assignment {}?",
                "When do I need to submit {}?",
                "Is {} due this week?",
            ],
            "late_policy": [
                "What is the late policy?",
                "How many late days do I have?",
                "Can I submit late?",
                "What happens if I miss the deadline?",
                "How do late days work?",
            ],
            "pointers": [
                "I don't understand pointers",
                "How do pointers work in C?",
                "What's the difference between * and &?",
                "Why am I getting a segmentation fault?",
                "Help with pointer arithmetic",
                "My pointer code isn't working",
            ],
            "malloc": [
                "How do I use malloc?",
                "What's the difference between malloc and calloc?",
                "Do I need to free memory?",
                "Getting malloc errors",
                "Memory allocation help",
                "When should I use malloc?",
            ],
            "arrays": [
                "How do arrays work in C?",
                "Array vs pointer confusion",
                "How to pass arrays to functions?",
                "Array indexing help",
                "Multi-dimensional arrays?",
            ],
            "debugging": [
                "How do I debug my code?",
                "What debugging tools should I use?",
                "My code compiles but doesn't work",
                "How to find bugs?",
                "Debugging strategies?",
            ],
            "mario": [
                "Stuck on Mario problem",
                "How do I print the pyramid?",
                "Mario nested loops help",
                "Can't get Mario output right",
            ],
            "caesar": [
                "Caesar cipher help",
                "How to rotate characters?",
                "Caesar algorithm explanation",
                "Stuck on Caesar problem",
            ],
        }
        
        # Artifacts (assignments/topics)
        self.artifacts = [
            "Problem Set 1",
            "Problem Set 2", 
            "Problem Set 3",
            "Lecture 1",
            "Lecture 2",
            "Lecture 3",
            "Syllabus",
        ]
    
    def generate_demo_data(self, num_questions: int = 50):
        """Generate comprehensive demo data"""
        print(f"🎲 Generating {num_questions} mock questions...")
        
        # Generate questions over the past 7 days
        for i in range(num_questions):
            self._generate_random_question(days_ago=random.randint(0, 7))
        
        print(f"✅ Generated {num_questions} questions")
        print(f"   Clusters: {len(self.service.clusters)}")
        print(f"   Unresolved: {len([item for item in self.service.unresolved_queue.values() if not item.resolved])}")
        print(f"   Confusion signals: {len(self.service.confusion_signals)}")
    
    def _generate_random_question(self, days_ago: int = 0):
        """Generate a single random question"""
        # Pick random student
        student = random.choice(self.students)
        
        # Pick topic based on student level
        if student["level"] == "struggling":
            # Struggling students ask more about difficult topics
            topic = random.choice(["pointers", "malloc", "debugging", "mario", "caesar"])
        elif student["level"] == "silent":
            # Silent students rarely ask questions
            if random.random() > 0.9:  # 10% chance
                topic = random.choice(["deadlines", "late_policy"])
            else:
                return  # Don't generate question
        else:
            # Average/thriving students ask varied questions
            topic = random.choice(list(self.question_templates.keys()))
        
        # Generate question
        question_template = random.choice(self.question_templates[topic])
        if "{}" in question_template:
            question = question_template.format(random.randint(1, 3))
        else:
            question = question_template
        
        # Determine artifact
        if topic in ["mario", "caesar"]:
            artifact = f"Problem Set {random.randint(1, 2)}"
        elif topic in ["pointers", "malloc", "arrays"]:
            artifact = f"Lecture {random.randint(1, 3)}"
        else:
            artifact = random.choice(self.artifacts)
        
        # Determine confidence based on topic and student level
        if topic in ["pointers", "malloc", "debugging"] and student["level"] == "struggling":
            confidence = random.uniform(0.3, 0.5)  # Low confidence
        elif topic in ["deadlines", "late_policy"]:
            confidence = random.uniform(0.8, 0.95)  # High confidence
        else:
            confidence = random.uniform(0.6, 0.8)  # Medium confidence
        
        # Generate response
        response = f"Here's information about {topic}..."
        
        # Adjust timestamp
        timestamp = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))
        
        # Log the question
        self.service.log_question(
            student_id=student["id"],
            question=question,
            artifact=artifact,
            section=topic.replace("_", " ").title(),
            confidence=confidence,
            response=response
        )
        
        # Add confusion signals for struggling students
        if student["level"] == "struggling" and confidence < 0.6:
            self.service.log_confusion_signal(
                student_id=student["id"],
                artifact=artifact,
                section=topic.replace("_", " ").title(),
                question=question,
                signal_type="low_confidence"
            )
    
    def get_student_personas(self):
        """Return student personas for demo"""
        return self.students
    
    def generate_content_gaps(self):
        """Identify content gaps from generated data"""
        gaps = []
        
        # Analyze low-confidence questions
        low_conf_by_topic = {}
        for log in self.service.question_logs:
            if log["confidence"] < 0.6:
                topic = log.get("section", "Unknown")
                if topic not in low_conf_by_topic:
                    low_conf_by_topic[topic] = []
                low_conf_by_topic[topic].append(log["question"])
        
        # Create gap reports
        for topic, questions in low_conf_by_topic.items():
            if len(questions) >= 3:  # At least 3 low-confidence questions
                gaps.append({
                    "topic": topic,
                    "question_count": len(questions),
                    "example_questions": questions[:3],
                    "suggested_action": f"Consider adding more material about {topic}",
                    "priority": "high" if len(questions) > 5 else "medium"
                })
        
        return sorted(gaps, key=lambda x: x["question_count"], reverse=True)


def seed_demo_data(professor_service: ProfessorService):
    """Seed the system with demo data"""
    generator = MockDataGenerator(professor_service)
    generator.generate_demo_data(num_questions=50)
    
    # Create demo clusters with published canonical answers
    from models import CreateCanonicalAnswerRequest, Citation
    import uuid
    from datetime import datetime
    
    demo_clusters_with_answers = [
        {
            "cluster_id": "answered_1",
            "representative_question": "How do I allocate memory with malloc?",
            "count": 42,
            "artifact": "Pointers",
            "section": "Week 3",
            "answer": "Memory allocation in C uses malloc() to dynamically allocate memory on the heap. You need to include <stdlib.h> and remember to free the memory when done to avoid memory leaks.",
            "similar_questions": [
                "What is malloc used for?",
                "How to allocate memory in C?",
                "Difference between malloc and calloc?",
                "Why do I need to free memory?",
                "How much memory does malloc allocate?"
            ]
        },
        {
            "cluster_id": "answered_2",
            "representative_question": "What is the difference between arrays and pointers?",
            "count": 28,
            "artifact": "Pointers",
            "section": "Week 3",
            "answer": "Arrays and pointers are closely related in C. An array name is essentially a pointer to the first element. However, arrays have fixed size and pointers can be reassigned.",
            "similar_questions": [
                "Are arrays and pointers the same?",
                "Can I use array notation with pointers?",
                "Why does array[i] equal *(array + i)?",
                "Can I reassign an array name?",
                "What is pointer arithmetic?"
            ]
        },
        {
            "cluster_id": "answered_3",
            "representative_question": "How do I debug segmentation faults?",
            "count": 35,
            "artifact": "Debugging",
            "section": "Week 4",
            "answer": "Segmentation faults occur when you access memory you shouldn't. Use valgrind to detect memory errors, check array bounds, ensure pointers are initialized, and verify malloc succeeded.",
            "similar_questions": [
                "What causes segfaults?",
                "How to fix segmentation fault?",
                "Why does my program crash with segfault?",
                "How to use valgrind?",
                "What is a null pointer dereference?"
            ]
        }
    ]
    
    # Create clusters and canonical answers (only if they don't already exist)
    for demo_cluster in demo_clusters_with_answers:
        cluster_id = demo_cluster["cluster_id"]
        
        # Skip if cluster already exists
        if cluster_id in professor_service.clusters:
            # Check if it already has a published answer
            existing_cluster = professor_service.clusters[cluster_id]
            if existing_cluster.canonical_answer_id:
                existing_answer = professor_service.canonical_answers.get(existing_cluster.canonical_answer_id)
                if existing_answer and existing_answer.is_published:
                    continue  # Already seeded, skip
        
        # Create cluster
        from models import QuestionCluster
        cluster = QuestionCluster(
            cluster_id=cluster_id,
            representative_question=demo_cluster["representative_question"],
            similar_questions=demo_cluster["similar_questions"],
            count=demo_cluster["count"],
            artifact=demo_cluster["artifact"],
            section=demo_cluster["section"],
            canonical_answer_id=None,  # Will be set after creating answer
            created_at=datetime.now(),
            last_seen=datetime.now()
        )
        professor_service.clusters[cluster_id] = cluster
        
        # Create canonical answer
        request = CreateCanonicalAnswerRequest(
            cluster_id=cluster_id,
            question=demo_cluster["representative_question"],
            answer_markdown=demo_cluster["answer"],
            citations=[]
        )
        canonical = professor_service.create_canonical_answer(request, "prof1")
        
        # Publish the answer
        professor_service.publish_canonical_answer(canonical.answer_id)
    
    return generator
