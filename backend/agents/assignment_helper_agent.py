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
        """Generate Socratic hints and guidance using LLM"""
        # Get OpenAI tool
        openai_tool = self.get_tool("openai")
        if not openai_tool:
            # Fallback to hardcoded guidance if OpenAI not available
            self.log("⚠️  OpenAI tool not available, using fallback templates", "WARNING")
            return self._generate_fallback_guidance(question, retrieved_chunks)
        
        self.log("✅ OpenAI tool found, generating LLM-powered guidance", "INFO")
        
        # Build context from retrieved chunks
        context_text = "\n\n".join([chunk[0].text for chunk in retrieved_chunks[:3]])
        
        # Determine question type for specialized prompting
        question_lower = question.lower()
        question_type = self._classify_question(question_lower)
        
        # Create specialized system prompt with strong guardrails
        system_prompt = self._create_assignment_helper_prompt(question_type)
        
        try:
            # Generate guidance using LLM
            self.log(f"🤖 Calling OpenAI API for question type: {question_type}", "INFO")
            guidance = await openai_tool.execute({
                'question': question,
                'context': context_text,
                'system_prompt': system_prompt,
                'max_tokens': 800
            })
            self.log(f"✅ LLM response received ({len(guidance)} chars)", "INFO")
            
            # Extract concepts from chunks and guidance
            concepts = self._extract_concepts(retrieved_chunks)
            
            # Generate resources and next steps
            resources = self._suggest_resources(question_type)
            next_steps = self._suggest_next_steps(question_type)
            
            return guidance, concepts, resources, next_steps
            
        except Exception as e:
            self.log(f"Error generating LLM guidance: {str(e)}", "ERROR")
            return self._generate_fallback_guidance(question, retrieved_chunks)
    
    def _classify_question(self, question_lower: str) -> str:
        """Classify the type of question being asked"""
        if any(word in question_lower for word in ['error', 'bug', 'wrong', 'not working', "doesn't work"]):
            return 'debugging'
        elif any(word in question_lower for word in ['how do i', 'how to', 'implement', 'write']):
            return 'implementation'
        elif any(word in question_lower for word in ['understand', 'confused', 'what is', 'explain']):
            return 'conceptual'
        elif any(word in question_lower for word in ['start', 'begin', 'getting started']):
            return 'getting_started'
        else:
            return 'general'
    
    def _create_assignment_helper_prompt(self, question_type: str) -> str:
        """Create specialized system prompt based on question type with strong guardrails"""
        base_prompt = """You are OpenTA, an AI teaching assistant for CS50. This is a GRADED ASSIGNMENT.

🚨 CRITICAL GUARDRAILS - YOU MUST FOLLOW THESE:
1. NEVER provide complete code solutions or direct answers
2. NEVER write code that solves the problem for the student
3. NEVER give step-by-step implementation details that would constitute doing the work for them
4. Use the Socratic method - guide with questions, not answers
5. Help students think through problems, don't think for them
6. If asked for "the answer" or "the code", politely refuse and redirect to learning

Your role is to:
- Ask guiding questions that help students discover solutions themselves
- Point to relevant concepts and resources
- Help debug by teaching debugging strategies, not fixing their code
- Encourage critical thinking and problem-solving skills
- Be supportive and encouraging while maintaining academic integrity
"""
        
        if question_type == 'debugging':
            return base_prompt + """\nFor debugging questions:
- Ask what they expected vs what happened
- Suggest debugging techniques (print statements, step-through debugging)
- Guide them to identify the problem area themselves
- Ask about their testing approach
- NEVER fix their code directly"""
        
        elif question_type == 'implementation':
            return base_prompt + """\nFor implementation questions:
- Ask about their understanding of the problem requirements
- Suggest breaking the problem into smaller steps
- Point to relevant concepts from course materials
- Ask what approaches they've considered
- Encourage pseudocode before coding
- NEVER provide actual code implementations"""
        
        elif question_type == 'conceptual':
            return base_prompt + """\nFor conceptual questions:
- Explain concepts clearly using analogies and examples
- Connect to material they've already learned
- Ask questions to check their understanding
- Suggest working through examples by hand
- You can be more direct with concepts, but still encourage active learning"""
        
        elif question_type == 'getting_started':
            return base_prompt + """\nFor getting started questions:
- Help them understand the problem requirements
- Suggest breaking down the problem
- Ask about inputs, outputs, and constraints
- Encourage planning before coding
- Point to relevant examples from lectures
- NEVER provide a solution outline that's too detailed"""
        
        else:
            return base_prompt + """\nFor general questions:
- Clarify what they're asking
- Guide them to be more specific
- Suggest resources and approaches
- Encourage breaking down the problem"""
    
    def _suggest_resources(self, question_type: str) -> list:
        """Suggest relevant resources based on question type"""
        base_resources = ['Review assignment specification', 'Check lecture notes']
        
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
    
    def _suggest_next_steps(self, question_type: str) -> list:
        """Suggest next steps based on question type"""
        if question_type == 'debugging':
            return [
                'Identify the exact line where the problem occurs',
                'Add print statements to track variable values',
                'Test with simple inputs first',
                'Check if your logic handles all cases'
            ]
        elif question_type == 'implementation':
            return [
                'Write pseudocode first',
                'Break the problem into smaller functions',
                'Start with the simplest version',
                'Test each part independently'
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
                'Clarify what specifically you need help with',
                'Review the problem requirements',
                'Break down the problem into smaller parts',
                'Ask more specific questions'
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
