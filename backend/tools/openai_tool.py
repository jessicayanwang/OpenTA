"""
OpenAI Tool
Uses OpenAI API to generate high-quality answers
"""
from typing import Dict, Any, List
from .base_tool import BaseTool
import os
from openai import OpenAI

class OpenAITool(BaseTool):
    """
    Tool for generating answers using OpenAI's GPT models
    """
    
    def __init__(self, api_key: str = None):
        super().__init__(
            name="openai",
            description="Generate high-quality answers using OpenAI GPT"
        )
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")
        
        # Initialize OpenAI client without proxies parameter
        self.client = OpenAI(
            api_key=self.api_key,
            timeout=30.0,
            max_retries=2
        )
        self.model = "gpt-4o-mini"  # Fast and cost-effective
    
    async def execute(self, params: Dict[str, Any]) -> str:
        """
        Generate answer using OpenAI
        
        Params:
            question (str): The student's question
            context (str): Retrieved context from documents
            system_prompt (str): Optional system prompt
            max_tokens (int): Maximum response length (default: 500)
        """
        if not self.validate_params(params, ['question', 'context']):
            raise ValueError("Missing required parameters: question, context")
        
        question = params['question']
        context = params['context']
        system_prompt = params.get('system_prompt', self._default_system_prompt())
        max_tokens = params.get('max_tokens', 500)
        
        try:
            # Create messages for chat completion
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": self._format_user_message(question, context)}
            ]
            
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.7,
                top_p=0.9
            )
            
            # Extract answer
            answer = response.choices[0].message.content.strip()
            
            return answer
            
        except Exception as e:
            # Fallback to context if API fails
            print(f"OpenAI API error: {str(e)}")
            return self._fallback_answer(context)
    
    def _default_system_prompt(self) -> str:
        """Default system prompt for OpenTA"""
        return """You are OpenTA, an AI teaching assistant for CS50 (Introduction to Computer Science).

Your role is to:
1. Answer student questions clearly and accurately based on the provided course materials
2. Be helpful and encouraging
3. Cite the source of information when relevant
4. If the context doesn't contain the answer, say so honestly

Guidelines:
- Keep answers concise but complete
- Use appropriate formatting (bullet points, code blocks, etc.)
- Be friendly and supportive
- Never make up information not in the context
- For policy questions, quote the exact policy
- For deadline questions, provide the specific date and time"""
    
    def _format_user_message(self, question: str, context: str) -> str:
        """Format the user message with question and context"""
        return f"""Based on the following course materials, please answer the student's question.

COURSE MATERIALS:
{context}

STUDENT QUESTION:
{question}

Please provide a clear, accurate answer based on the course materials above. If the materials don't contain enough information to answer the question, say so."""
    
    def _fallback_answer(self, context: str) -> str:
        """Fallback answer if API fails"""
        return f"Based on the course materials:\n\n{context[:300]}..."
