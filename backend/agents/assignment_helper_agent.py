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
                guidance, concepts, resources, next_steps = self._generate_socratic_guidance(
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
    
    def _generate_socratic_guidance(self, question, problem_number, context, retrieved_chunks):
        """Generate Socratic hints and guidance"""
        question_lower = question.lower()
        
        # Analyze question type
        if any(word in question_lower for word in ['error', 'bug', 'wrong', 'not working']):
            guidance = self._debug_guidance(question, context)
            concepts = ['Debugging', 'Error Analysis', 'Testing']
            resources = ['Review debugging strategies', 'Check your logic step by step']
            next_steps = [
                'Add print statements to see variable values',
                'Test with simple inputs first',
                'Review the problem requirements'
            ]
        
        elif any(word in question_lower for word in ['how do i', 'how to', 'implement']):
            guidance = self._implementation_guidance(question, retrieved_chunks)
            concepts = self._extract_concepts(retrieved_chunks)
            resources = ['Review lecture notes on this topic', 'Check the assignment specification']
            next_steps = [
                'Break the problem into smaller steps',
                'Write pseudocode first',
                'Test each part independently'
            ]
        
        elif any(word in question_lower for word in ['understand', 'confused', 'what is']):
            guidance = self._conceptual_guidance(question, retrieved_chunks)
            concepts = self._extract_concepts(retrieved_chunks)
            resources = ['Review relevant lecture materials', 'Try working through examples']
            next_steps = [
                'Draw out the problem on paper',
                'Work through a simple example',
                'Identify what you do understand'
            ]
        
        else:
            guidance = self._general_guidance(question, retrieved_chunks)
            concepts = self._extract_concepts(retrieved_chunks)
            resources = ['Review the assignment specification']
            next_steps = [
                'Clarify what you\'re trying to achieve',
                'Break down the problem',
                'Start with a simple approach'
            ]
        
        return guidance, concepts, resources, next_steps
    
    def _debug_guidance(self, question, context):
        """Provide debugging guidance"""
        return (
            "🔍 Let's debug this together! Instead of giving you the answer, let me guide you:\n\n"
            "1. **What is the expected behavior?** What should your code do?\n"
            "2. **What is actually happening?** Describe the error or unexpected output.\n"
            "3. **Where might the issue be?** Can you narrow down which part of your code might be causing this?\n\n"
            "Try adding print statements to see what values your variables have at different points. "
            "This will help you identify where things go wrong."
        )
    
    def _implementation_guidance(self, question, chunks):
        """Provide implementation guidance"""
        if chunks:
            chunk_text = chunks[0][0].text[:200]
            return (
                f"💡 Great question! Let's think through this step by step:\n\n"
                f"According to the assignment: \"{chunk_text}...\"\n\n"
                f"**Guiding Questions:**\n"
                f"1. What are the inputs and outputs?\n"
                f"2. What steps do you need to take to transform the input into the output?\n"
                f"3. Can you write pseudocode for each step?\n\n"
                f"Try breaking this down into smaller functions or steps. What would be the first thing you need to do?"
            )
        else:
            return (
                "💡 Let's approach this systematically:\n\n"
                "1. What are you trying to accomplish?\n"
                "2. What tools or concepts might help?\n"
                "3. Can you break it into smaller steps?\n\n"
                "Start with the simplest version first, then add complexity."
            )
    
    def _conceptual_guidance(self, question, chunks):
        """Provide conceptual understanding guidance"""
        return (
            "🤔 Let's build your understanding:\n\n"
            "1. **What do you already know** about this concept?\n"
            "2. **What specific part** is confusing?\n"
            "3. **Can you explain it in your own words?**\n\n"
            "Try working through a simple example by hand first. "
            "Understanding the concept before coding will make implementation much easier!"
        )
    
    def _general_guidance(self, question, chunks):
        """Provide general guidance"""
        return (
            "🎯 Let's work through this together:\n\n"
            "**Think about:**\n"
            "- What is the problem asking you to do?\n"
            "- What tools or concepts from class might help?\n"
            "- What would a simple solution look like?\n\n"
            "Remember: Start simple, test often, and build up complexity gradually."
        )
    
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
