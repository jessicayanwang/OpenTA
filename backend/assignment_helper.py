"""
Assignment Helper Agent
Provides Socratic guidance to help students learn without giving direct answers
"""
from typing import List, Tuple
from document_store import DocumentChunk
from models import Citation, AssignmentHelpRequest, AssignmentHelpResponse

class AssignmentHelper:
    """
    Helps students with assignments using Socratic method
    Provides hints, asks guiding questions, and points to concepts
    Never gives direct answers or complete solutions
    """
    
    def __init__(self):
        pass
    
    def help_with_assignment(
        self, 
        request: AssignmentHelpRequest,
        retrieved_chunks: List[Tuple[DocumentChunk, float]]
    ) -> AssignmentHelpResponse:
        """
        Generate helpful guidance without giving direct answers
        """
        if not retrieved_chunks:
            return self._generate_generic_help(request)
        
        # Build citations from retrieved chunks
        citations = []
        for i, (chunk, score) in enumerate(retrieved_chunks):
            citation_text = chunk.text
            if len(chunk.text) > 500:
                truncated = chunk.text[:500]
                last_period = truncated.rfind('.')
                if last_period > 300:
                    citation_text = chunk.text[:last_period + 1] + "..."
                else:
                    citation_text = truncated + "..."
            
            citations.append(Citation(
                source=chunk.source,
                section=chunk.section,
                text=citation_text,
                relevance_score=score
            ))
        
        # Analyze the question and generate appropriate guidance
        guidance, concepts, resources, next_steps = self._generate_socratic_guidance(
            request, retrieved_chunks
        )
        
        return AssignmentHelpResponse(
            guidance=guidance,
            concepts=concepts,
            resources=resources,
            next_steps=next_steps,
            citations=citations
        )
    
    def _generate_socratic_guidance(
        self,
        request: AssignmentHelpRequest,
        retrieved_chunks: List[Tuple[DocumentChunk, float]]
    ) -> Tuple[str, List[str], List[str], List[str]]:
        """Generate guidance using Socratic questioning approach"""
        
        question = request.question.lower()
        context = request.context.lower() if request.context else ""
        top_chunk = retrieved_chunks[0][0] if retrieved_chunks else None
        
        # Identify the type of help needed
        if any(word in question for word in ['how to start', 'where to begin', 'getting started']):
            return self._help_getting_started(request, top_chunk)
        
        elif any(word in question for word in ['error', 'bug', 'wrong', "doesn't work", 'not working']):
            return self._help_debugging(request, top_chunk)
        
        elif any(word in question for word in ['algorithm', 'logic', 'approach', 'how to solve']):
            return self._help_algorithm_design(request, top_chunk)
        
        elif any(word in question for word in ['syntax', 'write', 'code', 'implement']):
            return self._help_implementation(request, top_chunk)
        
        elif any(word in question for word in ['understand', 'what is', 'explain', 'meaning']):
            return self._help_concept_understanding(request, top_chunk)
        
        else:
            return self._help_general(request, top_chunk)
    
    def _help_getting_started(self, request: AssignmentHelpRequest, chunk: DocumentChunk) -> Tuple[str, List[str], List[str], List[str]]:
        """Help student get started on a problem"""
        
        guidance = """🎯 **Great question! Let's break this down step by step.**

Before writing any code, it's important to understand the problem fully. Let me guide you:

**Questions to ask yourself:**
1. What is the program supposed to do? (Read the requirements carefully)
2. What inputs does the program need from the user?
3. What should the program output?
4. Are there any special conditions or constraints?

**Think about:**
- What are the main steps your program needs to perform?
- Can you describe the solution in plain English first?
- What examples are given, and can you trace through them manually?

Remember: Programming is about problem-solving first, coding second! 🧠"""
        
        concepts = [
            "Problem decomposition",
            "Input/Output analysis",
            "Requirements gathering",
            "Algorithm design basics"
        ]
        
        resources = [
            "Review the problem requirements carefully",
            "Look at the example outputs provided",
            "Check lecture notes on program structure",
            "Review shorts on the relevant topic"
        ]
        
        next_steps = [
            "Write out the problem in your own words",
            "List all inputs and expected outputs",
            "Sketch out the main steps in pseudocode",
            "Only then start writing actual code"
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _help_debugging(self, request: AssignmentHelpRequest, chunk: DocumentChunk) -> Tuple[str, List[str], List[str], List[str]]:
        """Help student debug their code"""
        
        guidance = """🐛 **Debugging is a crucial skill! Let's troubleshoot systematically.**

**Debugging Strategy:**

1. **Understand the error:**
   - What error message are you seeing? (Read it carefully!)
   - At what line does it occur?
   - What were you trying to do at that point?

2. **Use debugging tools:**
   - Add `printf` statements to check variable values
   - Use the debugger to step through code line by line
   - Check boundary cases (what if input is 0? negative? very large?)

3. **Common issues to check:**
   - Are your variables initialized?
   - Are you using the right operators (= vs ==)?
   - Are your loop conditions correct?
   - Are you checking for the right conditions?

**Think about:** What did you expect to happen vs. what actually happened?"""
        
        concepts = [
            "Debugging techniques",
            "Reading error messages",
            "Variable tracking",
            "Edge case testing"
        ]
        
        resources = [
            "Use check50 to test your code",
            "Review debugging tips in lecture notes",
            "Use printf debugging or debugger50",
            "Post on Ed Discussion (describe what you tried)"
        ]
        
        next_steps = [
            "Identify the exact line where the problem occurs",
            "Print out variable values before that line",
            "Test with simple inputs first",
            "Check if your logic handles all cases"
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _help_algorithm_design(self, request: AssignmentHelpRequest, chunk: DocumentChunk) -> Tuple[str, List[str], List[str], List[str]]:
        """Help student design their algorithm"""
        
        guidance = """💡 **Let's think about the algorithm logically!**

**Design Process:**

1. **Break down the problem:**
   - What are the major steps?
   - Can you solve a simpler version first?
   
2. **Think about the logic:**
   - Do you need loops? Which kind (for, while)?
   - Do you need conditions? What are they?
   - What data structures might help?

3. **Work through an example:**
   - Take a sample input
   - Manually work through what needs to happen
   - This becomes your algorithm!

**Key Questions:**
- Can you describe each step in plain English?
- Have you handled all possible inputs?
- What's the simplest way to solve this?

Remember: A good algorithm is clear and handles all cases! 📝"""
        
        concepts = [
            "Algorithm design",
            "Control flow (loops, conditionals)",
            "Step-by-step problem solving",
            "Pattern recognition"
        ]
        
        resources = [
            "Review relevant lecture examples",
            "Look at similar problems from class",
            "Check shorts on loops and conditionals",
            "Draw flowcharts if helpful"
        ]
        
        next_steps = [
            "Write pseudocode for your approach",
            "Trace through your logic with sample inputs",
            "Identify patterns in the problem",
            "Start with the simplest version, then add complexity"
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _help_implementation(self, request: AssignmentHelpRequest, chunk: DocumentChunk) -> Tuple[str, List[str], List[str], List[str]]:
        """Help student with implementation details"""
        
        guidance = """⌨️ **Let's work on the implementation!**

**Implementation Tips:**

1. **Start simple:**
   - Get the basic structure working first
   - Add features one at a time
   - Test after each addition

2. **Syntax matters:**
   - Check your semicolons and brackets
   - Make sure variable types match
   - Follow the examples from lecture

3. **Build incrementally:**
   - Don't try to write everything at once
   - Compile frequently to catch errors early
   - Test with simple inputs before complex ones

**Questions to consider:**
- Have you reviewed similar code from lecture?
- Are you using the right C syntax for what you want to do?
- Have you tested each part independently?

Remember: Small steps lead to big solutions! 🪜"""
        
        concepts = [
            "C syntax and semantics",
            "Variable types and declarations",
            "Function structure",
            "Incremental development"
        ]
        
        resources = [
            "Review lecture code examples",
            "Check CS50 manual pages (man50)",
            "Look at shorts on C syntax",
            "Compile frequently with make"
        ]
        
        next_steps = [
            "Start with a basic skeleton that compiles",
            "Add one feature at a time",
            "Test with check50 after each major change",
            "Read compiler error messages carefully"
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _help_concept_understanding(self, request: AssignmentHelpRequest, chunk: DocumentChunk) -> Tuple[str, List[str], List[str], List[str]]:
        """Help student understand concepts"""
        
        guidance = """📚 **Understanding the concepts is key!**

**Learning Approach:**

1. **Connect to fundamentals:**
   - What basic concept is this building on?
   - Have you seen similar ideas before?
   - How does this relate to what you learned in lecture?

2. **Use concrete examples:**
   - Try working through a simple example by hand
   - What happens step by step?
   - Can you explain it to someone else?

3. **Practice makes perfect:**
   - The more you work with the concept, the clearer it becomes
   - Try variations of the problem
   - Explain the concept in your own words

**Think about:** Why does this concept matter? Where might you use it?"""
        
        concepts = [
            "Foundational programming concepts",
            "Problem-solving patterns",
            "Computational thinking"
        ]
        
        resources = [
            "Re-watch relevant lecture sections",
            "Review shorts and walkthroughs",
            "Read CS50 study materials",
            "Discuss with classmates (no code sharing!)"
        ]
        
        next_steps = [
            "Identify what specifically is unclear",
            "Review prerequisite concepts if needed",
            "Work through examples manually",
            "Try explaining the concept in your own words"
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _help_general(self, request: AssignmentHelpRequest, chunk: DocumentChunk) -> Tuple[str, List[str], List[str], List[str]]:
        """Provide general help"""
        
        guidance = """👋 **I'm here to help you learn!**

Instead of giving you the answer directly, let me help you think through this:

**Let's start with:**
1. What have you tried so far?
2. What specific part is challenging you?
3. What do you understand about the problem so far?

**General tips:**
- Break the problem into smaller pieces
- Test your understanding with simple examples
- Don't hesitate to review lecture materials
- Use the debugging tools available to you

Remember: Struggling is part of learning! Each challenge makes you a better programmer. 💪

Can you tell me more specifically what you're stuck on?"""
        
        concepts = [
            "Problem-solving approach",
            "Learning strategies",
            "Debugging mindset"
        ]
        
        resources = [
            "Review assignment requirements",
            "Check lecture notes and shorts",
            "Use Ed Discussion for specific questions",
            "Attend office hours for personalized help"
        ]
        
        next_steps = [
            "Identify the specific area where you're stuck",
            "Review related course materials",
            "Try breaking the problem down further",
            "Ask more specific questions"
        ]
        
        return guidance, concepts, resources, next_steps
    
    def _generate_generic_help(self, request: AssignmentHelpRequest) -> AssignmentHelpResponse:
        """Generate help when no relevant documents are found"""
        
        guidance = """🤔 **I'd love to help, but I need more information!**

To give you the best guidance, I need to understand:
- Which specific problem are you working on?
- What have you tried so far?
- What's the specific challenge you're facing?

**In the meantime, here are general tips:**
- Read the problem requirements carefully
- Start with the simplest approach
- Test with basic inputs first
- Use the debugging tools available

Remember: Good questions lead to good learning! Try being more specific about what you need help with."""
        
        return AssignmentHelpResponse(
            guidance=guidance,
            concepts=["Problem identification", "Asking good questions"],
            resources=["Assignment specification", "Lecture materials", "Ed Discussion"],
            next_steps=["Clarify your specific question", "Review problem requirements"],
            citations=[]
        )
