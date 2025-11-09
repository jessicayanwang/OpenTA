"""
Guardrail Tool
Checks and enforces course guardrails
"""
from typing import Dict, Any
from .base_tool import BaseTool

class GuardrailTool(BaseTool):
    """
    Tool for checking and enforcing guardrails
    """
    
    def __init__(self, professor_service):
        super().__init__(
            name="guardrail",
            description="Check and enforce course guardrails and policies"
        )
        self.professor_service = professor_service
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check guardrails
        
        Params:
            check_type (str): Type of check (hint_limit, graded_assignment, etc.)
            course_id (str): Course ID
            student_id (str): Student ID
            assignment_id (str): Assignment ID (optional)
        """
        if not self.validate_params(params, ['check_type', 'course_id']):
            raise ValueError("Missing required parameters: check_type, course_id")
        
        check_type = params['check_type']
        course_id = params['course_id']
        
        settings = self.professor_service.get_guardrail_settings(course_id)
        
        result = {
            "allowed": True,
            "message": "",
            "settings": {}
        }
        
        if check_type == "hint_limit":
            student_id = params.get('student_id')
            assignment_id = params.get('assignment_id')
            
            # Get student's hint usage from memory (would be passed in)
            hint_count = params.get('current_hint_count', 0)
            max_hints = settings.max_hints
            
            result["settings"]["max_hints"] = max_hints
            result["settings"]["hints_used"] = hint_count
            result["settings"]["hints_remaining"] = max(0, max_hints - hint_count)
            
            if hint_count >= max_hints:
                result["allowed"] = False
                result["message"] = f"You've used all {max_hints} hints for this assignment."
        
        elif check_type == "graded_assignment":
            result["settings"]["banner_text"] = settings.graded_banner_text
            result["settings"]["show_thinking_path"] = settings.show_thinking_path
        
        return result
