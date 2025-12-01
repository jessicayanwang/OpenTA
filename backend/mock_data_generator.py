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
        
        # Get cluster count from database
        session = self.service.db.get_session()
        try:
            from database import QuestionClusterDB
            cluster_count = session.query(QuestionClusterDB).count()
            print(f"✅ Generated {num_questions} questions")
            print(f"   Clusters: {cluster_count}")
            print(f"   Unresolved: {len([item for item in self.service.unresolved_queue.values() if not item.resolved])}")
            print(f"   Confusion signals: {len(self.service.confusion_signals)}")
        finally:
            session.close()
    
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
        
        # Get question logs from database
        session = self.service.db.get_session()
        try:
            from database import QuestionLogDB
            question_logs = session.query(QuestionLogDB).all()
            
            # Analyze low-confidence questions
            low_conf_by_topic = {}
            for log in question_logs:
                if log.confidence < 0.6:
                    topic = log.section or "Unknown"
                    if topic not in low_conf_by_topic:
                        low_conf_by_topic[topic] = []
                    low_conf_by_topic[topic].append(log.question)
            
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
        finally:
            session.close()
    
    def generate_canonical_answers(self):
        """Generate canonical answers for some clusters to demo answered state"""
        from models import CreateCanonicalAnswerRequest, Citation
        
        # Predefined answers for common topics
        answer_templates = {
            "malloc": """# Memory Allocation with malloc()

The `malloc()` function dynamically allocates memory on the heap. Here's how to use it:

```c
int *ptr = (int*) malloc(sizeof(int) * 10);
if (ptr == NULL) {
    // Handle allocation failure
    return 1;
}
// Use the memory
ptr[0] = 42;

// Always free when done!
free(ptr);
```

**Key Points:**
- Always check if malloc returns NULL (allocation failed)
- Use `sizeof()` to calculate the right amount of memory
- Always `free()` the memory when done to prevent memory leaks
- `calloc()` is similar but initializes memory to zero""",
            
            "pointers": """# Understanding Pointers in C

Pointers store memory addresses. Think of them as "arrows" pointing to data:

```c
int x = 42;      // Regular variable
int *p = &x;     // Pointer storing address of x
printf("%d", *p); // Prints 42 (dereference pointer)
```

**Key Operators:**
- `&` - Address-of operator (gets memory address)
- `*` - Dereference operator (accesses value at address)

**Common Use Cases:**
- Dynamic memory allocation
- Passing large data structures efficiently
- Implementing data structures (linked lists, trees)
- String manipulation""",
            
            "arrays": """# Arrays in C

Arrays are contiguous blocks of memory holding elements of the same type:

```c
int arr[5] = {1, 2, 3, 4, 5};
arr[0] = 10;  // Access first element
```

**Array vs Pointer:**
- Array name is a pointer to the first element
- `arr[i]` is equivalent to `*(arr + i)`
- Arrays have fixed size, pointers can be reassigned

**Passing to Functions:**
```c
void printArray(int arr[], int size) {
    for (int i = 0; i < size; i++) {
        printf("%d ", arr[i]);
    }
}
```""",
            
            "debugging": """# Debugging Strategies in C

**Step-by-step approach:**

1. **Use printf statements** - Add debug prints to track values
2. **Use a debugger (GDB)** - Set breakpoints and step through code
3. **Check for common errors:**
   - Uninitialized variables
   - Array bounds violations
   - Null pointer dereferences
   - Memory leaks

**GDB Quick Guide:**
```bash
gcc -g myfile.c -o myprogram
gdb ./myprogram
(gdb) break main
(gdb) run
(gdb) print variable_name
(gdb) next
```

**Valgrind for Memory Errors:**
```bash
valgrind --leak-check=full ./myprogram
```""",
            
            "deadlines": """# Assignment Deadlines & Late Policy

**Standard Deadlines:**
- Problem sets are due on Fridays at 11:59 PM EST
- Check Canvas for specific due dates

**Late Policy:**
- You have **3 late days** total for the semester
- Use them wisely for unexpected situations
- After using all late days, late submissions receive 0 points

**Tips:**
- Start assignments early
- Attend office hours if stuck
- Don't wait until the last minute!
- Plan around midterms and other courses"""
        }
        
        # Get all clusters from database and answer about 40% of them
        # Use min_count=2 to match what frontend displays
        all_clusters = self.service.get_question_clusters("cs50", min_count=2)
        # Sort by count to answer the most popular ones
        all_clusters.sort(key=lambda x: x.count, reverse=True)
        
        # Answer only top 40% of clusters to ensure we have unanswered ones for testing
        num_to_answer = max(1, int(len(all_clusters) * 0.4))
        clusters_to_answer = all_clusters[:num_to_answer]
        
        print(f"📝 Creating canonical answers for {len(clusters_to_answer)} clusters...")
        
        for cluster in clusters_to_answer:
            # Find matching answer template based on artifact or section
            answer_text = None
            cluster_topic = (cluster.artifact or cluster.section or "").lower()
            
            for topic, template in answer_templates.items():
                if topic in cluster_topic:
                    answer_text = template
                    break
            
            # If no specific template, create a generic answer
            if not answer_text:
                answer_text = f"""# Answer to: {cluster.representative_question}

This is a comprehensive answer that addresses the core question.

**Key Points:**
- This answer has been verified by the teaching staff
- It covers the most common aspects of this question
- For more details, refer to the course materials

**Additional Resources:**
- Check the lecture slides
- Review the problem set specifications
- Attend office hours for clarification"""
            
            # Create canonical answer
            request = CreateCanonicalAnswerRequest(
                cluster_id=cluster.cluster_id,
                question=cluster.representative_question,
                answer_markdown=answer_text,
                citations=[]
            )
            
            self.service.create_canonical_answer(request, professor_id="prof_demo")
        
        print(f"✅ Created {len(clusters_to_answer)} canonical answers")


def seed_demo_data(professor_service: ProfessorService):
    """Seed the system with demo data"""
    generator = MockDataGenerator(professor_service)
    generator.generate_demo_data(num_questions=50)
    generator.generate_canonical_answers()  # Add answered clusters for demo
    return generator
