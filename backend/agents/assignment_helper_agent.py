"""
Assignment Helper Agent - Refactored for Multi-Agent Framework
Provides Socratic guidance without giving direct answers
Now with behavioral tracking and adaptive interventions
"""
import uuid
from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import AssignmentHelpResponse

class AssignmentHelperAgent(BaseAgent):
    """
    Specialized agent for helping with assignments using Socratic method
    Integrates behavioral tracking to detect struggle and offer interventions
    """
    
    def __init__(self, behavioral_tracker=None):
        super().__init__(
            agent_id="assignment_helper",
            name="Assignment Helper Agent",
            capabilities=[AgentCapability.PROVIDE_HINTS, AgentCapability.RETRIEVE_DOCUMENTS]
        )
        self.behavioral_tracker = behavioral_tracker
        self.active_sessions = {}  # Track session IDs per student
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process an assignment help request
        """
        try:
            content = message.content
            question = content.get('question', '')
            problem_number = content.get('problem_number')
            student_id = content.get('student_id', 'unknown')
            course_id = content.get('course_id', 'cs50')
            context = content.get('context', '')
            conversation_id = content.get('conversation_id', str(uuid.uuid4()))
            
            self.log(f"Processing assignment help: {question}")
            
            # Get student profile
            student_profile = self.memory.get_or_create_student_profile(student_id)
            
            # Start or continue behavioral tracking session
            session_id = self._get_or_create_session(student_id, problem_number or "general")
            
            # Log this as a question event in behavioral tracker
            if self.behavioral_tracker:
                self.behavioral_tracker.log_question(session_id, question)
                self.behavioral_tracker.update_time_on_task(session_id)
            
            # Check guardrails
            guardrail_tool = self.get_tool("guardrail")
            if guardrail_tool:
                assignment_id = problem_number or "general"
                hint_count = student_profile.get_hint_count(assignment_id)
                
                guardrail_check = await guardrail_tool.execute({
                    'check_type': 'hint_limit',
                    'course_id': course_id,
                    'student_id': student_id,
                    'assignment_id': assignment_id,
                    'current_hint_count': hint_count
                })
                
                if not guardrail_check['allowed']:
                    return self.create_response(
                        success=True,
                        data={
                            'help_response': {
                                'guidance': guardrail_check['message'],
                                'concepts': [],
                                'resources': ['Contact your instructor for additional help'],
                                'next_steps': ['Review the concepts covered so far'],
                                'citations': []
                            },
                            'hint_limit_reached': True
                        },
                        confidence=1.0
                    )
            
            # Use retrieval tool
            retrieval_tool = self.get_tool("retrieval")
            if not retrieval_tool:
                return self.create_response(
                    success=False,
                    data={},
                    error="Retrieval tool not available",
                    confidence=0.0
                )
            
            # Build search query
            search_query = f"{problem_number} {question}" if problem_number else question
            retrieved_chunks = await retrieval_tool.execute({
                'query': search_query,
                'top_k': 3
            })
            
            # Generate Socratic guidance
            if not retrieved_chunks:
                guidance, concepts, resources, next_steps = self._generate_generic_help(question)
                citations = []
            else:
                guidance, concepts, resources, next_steps = await self._generate_socratic_guidance(
                    question, problem_number, context, retrieved_chunks
                )
                
                # Use citation tool
                citation_tool = self.get_tool("citation")
                citations = await citation_tool.execute({
                    'chunks': retrieved_chunks
                }) if citation_tool else []
            
            # Update student profile
            if problem_number:
                student_profile.increment_hint_usage(problem_number)
            
            # Track hint request in behavioral tracker
            if self.behavioral_tracker:
                self.behavioral_tracker.log_hint_request(session_id)
            
            # Check if intervention should be offered
            intervention = None
            if self.behavioral_tracker:
                intervention = self.behavioral_tracker.should_offer_intervention(session_id)
            
            # Log analytics
            analytics_tool = self.get_tool("analytics")
            if analytics_tool:
                await analytics_tool.execute({
                    'event_type': 'question',
                    'student_id': student_id,
                    'data': {
                        'question': question,
                        'artifact': problem_number or 'assignment',
                        'confidence': 0.8,
                        'response': guidance
                    }
                })
            
            # Create response
            help_response = AssignmentHelpResponse(
                guidance=guidance,
                concepts=concepts,
                resources=resources,
                next_steps=next_steps,
                citations=citations
            )
            
            response_data = {
                'help_response': help_response.dict(),
                'conversation_id': conversation_id,
                'session_id': session_id
            }
            
            # Add intervention if recommended
            if intervention and intervention.get('offer'):
                response_data['intervention'] = intervention
                self.log(f"Offering intervention: {intervention.get('type')}")
            
            return self.create_response(
                success=True,
                data=response_data,
                confidence=0.8,
                reasoning="Provided Socratic guidance"
            )
            
        except Exception as e:
            self.log(f"Error processing assignment help: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _generate_socratic_guidance(self, question, problem_number, context, retrieved_chunks):
        """Generate scaffolded hints with progressive levels of help using LLM"""
        # Get OpenAI tool
        openai_tool = self.get_tool("openai")
        if not openai_tool:
            # Fallback to hardcoded guidance if OpenAI not available
            self.log("⚠️  OpenAI tool not available, using fallback templates", "WARNING")
            return self._generate_fallback_guidance(question, retrieved_chunks)
        
        self.log("✅ OpenAI tool found, generating LLM-powered guidance", "INFO")
        
        # Build context from retrieved chunks
        context_text = "\n\n".join([chunk[0].text for chunk in retrieved_chunks[:3]])
        
        # Determine question type and knowledge level
        question_lower = question.lower()
        
        # Detect if question is actually the problem description (prompt injection attempt)
        is_problem_description = self._is_problem_description(question_lower, context_text)
        if is_problem_description:
            self.log("⚠️  Detected problem description as question - applying strict guardrails", "WARNING")
        
        question_type = self._classify_question(question_lower)
        knowledge_level = self._detect_knowledge_level(question_lower)
        
        # Get hint count to determine scaffolding level
        student_id = "default_student"  # TODO: Get from session
        assignment_id = problem_number or "general"
        hint_count = self.memory.get_or_create_student_profile(student_id).get_hint_count(assignment_id)
        
        # Determine scaffolding level based on hint count
        # Hints 1-3: High level (Socratic questions)
        # Hints 4-7: Medium level (Structured guidance with examples)
        # Hints 8-10: Low level (Detailed guidance with pseudo-code)
        if hint_count < 3:
            scaffolding_level = "high"
        elif hint_count < 7:
            scaffolding_level = "medium"
        else:
            scaffolding_level = "low"
        
        self.log(f"📊 Hint #{hint_count + 1}, Scaffolding level: {scaffolding_level}, Knowledge: {knowledge_level}", "INFO")
        
        # Create specialized system prompt with scaffolding
        system_prompt = self._create_scaffolded_prompt(
            question_type, 
            scaffolding_level, 
            knowledge_level,
            problem_number,
            hint_count + 1,
            is_problem_description
        )
        
        try:
            # Generate guidance using LLM
            self.log(f"🤖 Calling OpenAI API for question type: {question_type}", "INFO")
            guidance = await openai_tool.execute({
                'question': question,
                'context': context_text,
                'system_prompt': system_prompt,
                'max_tokens': 1000
            })
            self.log(f"✅ LLM response received ({len(guidance)} chars)", "INFO")
            
            # Extract concepts from chunks and guidance
            concepts = self._extract_concepts(retrieved_chunks)
            
            # Generate resources and next steps based on scaffolding level
            resources = self._suggest_resources(question_type, scaffolding_level)
            next_steps = self._suggest_next_steps(question_type, scaffolding_level)
            
            return guidance, concepts, resources, next_steps
            
        except Exception as e:
            self.log(f"Error generating LLM guidance: {str(e)}", "ERROR")
            return self._generate_fallback_guidance(question, retrieved_chunks)
    
    def _is_problem_description(self, question_lower: str, context_text: str) -> bool:
        """Detect if the question is actually the problem description (prompt injection attempt)"""
        # Check for imperative verbs that indicate assignment instructions
        imperative_patterns = [
            "implement a program", "write a program", "create a program",
            "implement a function", "write a function", "create a function",
            "write code", "implement code", "create code",
            "your task is", "you must", "you should",
            "requirements:", "file name:", "must compile"
        ]
        
        # Check if question matches problem description patterns
        if any(pattern in question_lower for pattern in imperative_patterns):
            # Also check if it's similar to retrieved context (likely from assignment spec)
            if context_text and len(question_lower) > 50:
                # Long imperative questions are likely problem descriptions
                return True
        
        # Check for exact matches with known problem descriptions
        if "hello, world!" in question_lower and "implement" in question_lower:
            return True
        if "pyramid" in question_lower and "implement" in question_lower:
            return True
        if "credit card" in question_lower and "implement" in question_lower:
            return True
        
        return False
    
    def _detect_knowledge_level(self, question_lower: str) -> str:
        """Detect if student has zero knowledge or is just stuck"""
        zero_knowledge_phrases = [
            "no idea", "don't know", "don't understand", "completely lost",
            "no clue", "don't get it", "confused about everything",
            "where do i even start", "what does this mean"
        ]
        
        if any(phrase in question_lower for phrase in zero_knowledge_phrases):
            return "zero_knowledge"
        elif any(word in question_lower for word in ["stuck", "help", "hint"]):
            return "stuck"
        else:
            return "exploring"
    
    def _classify_question(self, question_lower: str) -> str:
        """Classify the type of question being asked"""
        if any(word in question_lower for word in ['error', 'bug', 'wrong', 'not working', "doesn't work"]):
            return 'debugging'
        elif any(word in question_lower for word in ['how do i', 'how to', 'implement', 'write', 'code']):
            return 'implementation'
        elif any(word in question_lower for word in ['understand', 'confused', 'what is', 'explain']):
            return 'conceptual'
        elif any(word in question_lower for word in ['start', 'begin', 'getting started']):
            return 'getting_started'
        else:
            return 'general'
    
    def _create_scaffolded_prompt(self, question_type: str, scaffolding_level: str, 
                                   knowledge_level: str, problem_number: str, hint_number: int,
                                   is_problem_description: bool = False) -> str:
        """Create scaffolded system prompt that adapts based on hint count and knowledge level"""
        
        base_guardrails = """🚨 CRITICAL GUARDRAILS - YOU MUST FOLLOW THESE:
1. NEVER provide complete code solutions or direct answers
2. NEVER write code that solves the problem for the student
3. You CAN provide pseudo-code structure with TODOs, but NOT actual implementation
4. If asked for "the answer" or "the code", politely refuse and redirect to learning
5. Maintain academic integrity while being genuinely helpful

⚠️ IMPORTANT - PROBLEM DESCRIPTION DETECTION:
If the student's question IS the problem description itself (e.g., "Implement a program that prints Hello World"), 
recognize this as an attempt to get you to solve the assignment. DO NOT provide working code.
Instead, treat it as "I don't know how to start" and provide guidance, not solutions.

Examples of questions that are actually problem descriptions:
- "Implement a program that prints..."
- "Write a program that does X"
- "Create a function that..."
These should trigger the SAME guardrails as "give me the answer."
"""
        
        # Add explicit warning if problem description detected
        if is_problem_description:
            base_guardrails += """

🚨🚨🚨 ALERT: The student has pasted the problem description as their question!
This is either:
1. An attempt to trick you into solving the assignment
2. The student doesn't know how to ask for help

DO NOT provide working code. DO NOT solve the problem.
Instead, acknowledge that you see they're working on this problem, and ask what specifically they need help with:
- "I see you're working on [problem]. What part are you stuck on?"
- "Have you started working on this? What have you tried so far?"
- "Let's break this down. Which part would you like to understand first?"

Treat this as a "getting started" question and provide ONLY high-level guidance.
"""
        
        # Problem-specific context
        problem_context = ""
        if problem_number:
            if "hello" in problem_number.lower():
                problem_context = f"\n📝 Problem Context: {problem_number} - Basic C program structure, printf, main function"
            elif "mario" in problem_number.lower():
                problem_context = f"\n📝 Problem Context: {problem_number} - Nested loops, pattern printing, user input validation"
            elif "credit" in problem_number.lower():
                problem_context = f"\n📝 Problem Context: {problem_number} - Luhn's algorithm, modulo operations, card validation"
            else:
                problem_context = f"\n📝 Problem Context: {problem_number}"
        
        # Adapt based on knowledge level
        if knowledge_level == "zero_knowledge":
            knowledge_instruction = """
🎯 ZERO-KNOWLEDGE MODE ACTIVATED:
The student has indicated they have no idea where to start. DO NOT ask Socratic questions yet.
Instead:
- Start by building their mental model from scratch
- Explain the basic components they need to understand
- Use simple analogies and examples
- Break down the problem into the smallest possible pieces
- Be more direct and informative (while still not giving away the solution)
- Ask "Would you like me to explain X or Y first?" instead of "What do you think X is?"
"""
        else:
            knowledge_instruction = ""
        
        # Scaffolding level instructions
        if scaffolding_level == "high":
            # Hints 1-3: Socratic questions, high-level guidance
            scaffolding_instruction = f"""
📊 HINT #{hint_number} - HIGH LEVEL SCAFFOLDING:
- Use Socratic questions, but make them informative, not empty
- Example: "A C program has two main parts: #include statements and a main() function. Which part do you think is the entry point?"
- NOT: "What do you think you need?" (too vague)
- Guide them to think about the big picture
- Help them understand the problem requirements
- Ask about their current understanding
"""
        elif scaffolding_level == "medium":
            # Hints 4-7: More structured guidance with examples
            scaffolding_instruction = f"""
📊 HINT #{hint_number} - MEDIUM LEVEL SCAFFOLDING:
- Provide more structure, but hide key implementation details
- You can describe what components are needed without showing how to implement them
- Example: "You'll need a loop that runs from 1 to height. Inside, you need to print spaces and then hashes. Can you think about how many of each?"
- Provide pseudo-code structure like:
  ```
  // Get input
  // TODO: prompt user
  
  // Process
  // TODO: your logic here
  
  // Output
  // TODO: print result
  ```
- Still encourage them to figure out the details
"""
        else:  # low
            # Hints 8-10: Detailed guidance with pseudo-code
            scaffolding_instruction = f"""
📊 HINT #{hint_number} - LOW LEVEL SCAFFOLDING:
- Provide detailed pseudo-code structure with TODOs
- Show the skeleton but not the implementation
- Example:
  ```c
  #include <...>  // TODO: what library for printf?
  
  int main(void)
  {{
      // TODO: declare variable for height
      
      // TODO: prompt user and get input
      
      // TODO: validate input (must be 1-8)
      
      // TODO: print the pyramid using nested loops
      
      return 0;
  }}
  ```
- Explain what each section needs to do
- Point to specific concepts they need (loops, conditionals, etc.)
- Still don't write the actual code for them
"""
        
        # Question type specific guidance
        type_guidance = ""
        if question_type == 'implementation':
            type_guidance = "\n💡 Implementation Question: Focus on breaking down the problem into steps and suggesting approaches."
        elif question_type == 'debugging':
            type_guidance = "\n🐛 Debugging Question: Teach debugging strategies, don't fix their code. Ask what they expected vs what happened."
        elif question_type == 'conceptual':
            type_guidance = "\n📚 Conceptual Question: You can be more direct in explaining concepts, use analogies and examples."
        elif question_type == 'getting_started':
            type_guidance = "\n🚀 Getting Started: Help them understand requirements and plan their approach."
        
        return f"""You are OpenTA, an AI teaching assistant for CS50. This is a GRADED ASSIGNMENT.

{base_guardrails}{problem_context}{knowledge_instruction}{scaffolding_instruction}{type_guidance}

Remember: Be supportive, encouraging, and genuinely helpful while maintaining academic integrity."""
    
    def _suggest_resources(self, question_type: str, scaffolding_level: str = "high") -> list:
        """Suggest relevant resources based on question type and scaffolding level"""
        base_resources = ['Review assignment specification', 'Check lecture notes']
        
        if scaffolding_level == "low":
            # More specific resources for students who need more help
            base_resources.append('CS50 manual pages for specific functions')
            base_resources.append('Work through lecture examples step-by-step')
        
        if question_type == 'debugging':
            return base_resources + ['Use debugger or print statements', 'Test with simple inputs', 'Check CS50 debugging guide']
        elif question_type == 'implementation':
            return base_resources + ['Review lecture code examples', 'Watch relevant shorts', 'Check CS50 manual pages']
        elif question_type == 'conceptual':
            return base_resources + ['Re-watch lecture sections', 'Review shorts', 'Work through examples']
        elif question_type == 'getting_started':
            return base_resources + ['Read problem requirements carefully', 'Look at example outputs']
        else:
            return base_resources + ['Post on Ed Discussion', 'Attend office hours']
    
    def _suggest_next_steps(self, question_type: str, scaffolding_level: str = "high") -> list:
        """Suggest next steps based on question type and scaffolding level"""
        if scaffolding_level == "high":
            # High-level next steps
            if question_type == 'debugging':
                return [
                    'Identify what you expected vs what happened',
                    'Think about where the logic might be wrong',
                    'Test with the simplest possible input'
                ]
            elif question_type == 'implementation':
                return [
                    'Understand the problem requirements fully',
                    'Think about the inputs and outputs',
                    'Consider what steps are needed'
                ]
            else:
                return [
                    'Break down the problem into smaller parts',
                    'Think about what you already know',
                    'Identify what you need to learn'
                ]
        elif scaffolding_level == "medium":
            # Medium-level next steps
            if question_type == 'debugging':
                return [
                    'Add print statements before the error line',
                    'Check variable values at each step',
                    'Test with edge cases (0, negative, very large)',
                    'Verify your loop conditions'
                ]
            elif question_type == 'implementation':
                return [
                    'Write pseudocode for your approach',
                    'Identify which C constructs you need (loops, conditionals)',
                    'Start with a simple version that handles one case',
                    'Test incrementally as you build'
                ]
            else:
                return [
                    'Sketch out the program structure',
                    'List the functions/tools you might need',
                    'Try a simple example by hand'
                ]
        else:  # low
            # Detailed next steps
            if question_type == 'debugging':
                return [
                    'Print each variable right before the error',
                    'Check: Are variables initialized? Are operators correct (= vs ==)?',
                    'Verify loop boundaries (off-by-one errors?)',
                    'Test with: smallest valid input, largest valid input, invalid input'
                ]
            elif question_type == 'implementation':
                return [
                    'Set up the basic program structure (includes, main function)',
                    'Add variable declarations for what you need to track',
                    'Implement input validation first',
                    'Add the core logic step by step',
                    'Test after each addition'
                ]
            elif question_type == 'conceptual':
                return [
                    'Work through a simple example by hand',
                    'Explain the concept in your own words',
                    'Connect to concepts you already know',
                    'Try variations of the problem'
                ]
            elif question_type == 'getting_started':
                return [
                    'List all inputs and expected outputs',
                    'Sketch out the main steps in pseudocode',
                    'Identify which concepts from class apply',
                    'Start with a basic skeleton'
                ]
            else:
                return [
                    'Create the file and basic structure',
                    'Add comments for each section you need',
                    'Implement one section at a time',
                    'Compile and test frequently'
                ]
    
    def _extract_concepts(self, chunks):
        """Extract key concepts from retrieved chunks"""
        if not chunks:
            return ['Problem Solving', 'Algorithm Design']
        
        # Simple keyword extraction
        concepts = []
        text = ' '.join([chunk[0].text.lower() for chunk in chunks])
        
        concept_keywords = {
            'loop': 'Loops',
            'array': 'Arrays',
            'function': 'Functions',
            'variable': 'Variables',
            'condition': 'Conditionals',
            'string': 'Strings',
            'algorithm': 'Algorithms'
        }
        
        for keyword, concept in concept_keywords.items():
            if keyword in text and concept not in concepts:
                concepts.append(concept)
        
        return concepts[:3] if concepts else ['Problem Solving', 'Programming Fundamentals']
    
    def _generate_fallback_guidance(self, question, retrieved_chunks):
        """Generate fallback guidance when LLM is not available"""
        question_lower = question.lower()
        question_type = self._classify_question(question_lower)
        
        # Use simple template-based guidance
        if question_type == 'debugging':
            guidance = (
                "🔍 Let's debug this together! Instead of giving you the answer, let me guide you:\n\n"
                "1. **What is the expected behavior?** What should your code do?\n"
                "2. **What is actually happening?** Describe the error or unexpected output.\n"
                "3. **Where might the issue be?** Can you narrow down which part of your code might be causing this?\n\n"
                "Try adding print statements to see what values your variables have at different points."
            )
        elif question_type == 'implementation':
            guidance = (
                "💡 Let's approach this systematically:\n\n"
                "1. What are you trying to accomplish?\n"
                "2. What tools or concepts might help?\n"
                "3. Can you break it into smaller steps?\n\n"
                "Start with the simplest version first, then add complexity."
            )
        elif question_type == 'conceptual':
            guidance = (
                "🤔 Let's build your understanding:\n\n"
                "1. **What do you already know** about this concept?\n"
                "2. **What specific part** is confusing?\n"
                "3. **Can you explain it in your own words?**\n\n"
                "Try working through a simple example by hand first."
            )
        else:
            guidance = (
                "🎯 Let's work through this together:\n\n"
                "**Think about:**\n"
                "- What is the problem asking you to do?\n"
                "- What tools or concepts from class might help?\n"
                "- What would a simple solution look like?\n\n"
                "Remember: Start simple, test often, and build up complexity gradually."
            )
        
        concepts = self._extract_concepts(retrieved_chunks)
        resources = self._suggest_resources(question_type)
        next_steps = self._suggest_next_steps(question_type)
        
        return guidance, concepts, resources, next_steps
    
    def _generate_generic_help(self, question):
        """Generate generic help when no specific information is found"""
        guidance = (
            "🤝 I'm here to help guide you! While I don't have specific information about this problem, "
            "let's work through it together:\n\n"
            "1. **Clarify the problem:** What are you trying to achieve?\n"
            "2. **Identify what you know:** What concepts from class might apply?\n"
            "3. **Break it down:** Can you split this into smaller steps?\n\n"
            "Feel free to ask more specific questions, or reach out to office hours for personalized help!"
        )
        
        concepts = ['Problem Solving', 'Critical Thinking']
        resources = ['Office hours', 'Course materials', 'Study groups']
        next_steps = [
            'Review the assignment specification',
            'Identify which concepts apply',
            'Start with a simple approach'
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _get_or_create_session(self, student_id: str, topic: str) -> str:
        """Get or create a behavioral tracking session for this student"""
        if not self.behavioral_tracker:
            return f"session_{student_id}_{uuid.uuid4().hex[:8]}"
        
        # Check if student has an active session
        if student_id in self.active_sessions:
            return self.active_sessions[student_id]
        
        # Create new session
        session_id = f"session_{student_id}_{uuid.uuid4().hex[:8]}"
        self.behavioral_tracker.start_session(session_id, student_id, topic)
        self.active_sessions[student_id] = session_id
        
        return session_id
    
    def end_student_session(self, student_id: str):
        """End a student's behavioral tracking session"""
        if student_id in self.active_sessions and self.behavioral_tracker:
            session_id = self.active_sessions[student_id]
            self.behavioral_tracker.end_session(session_id)
            del self.active_sessions[student_id]
