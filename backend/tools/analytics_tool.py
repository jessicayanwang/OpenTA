"""
Analytics Tool
Logs and analyzes student interactions
"""
from typing import Dict, Any
from .base_tool import BaseTool

class AnalyticsTool(BaseTool):
    """
    Tool for logging and analyzing student interactions
    """
    
    def __init__(self, professor_service):
        super().__init__(
            name="analytics",
            description="Log student interactions and analyze learning patterns"
        )
        self.professor_service = professor_service
    
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Log analytics event
        
        Params:
            event_type (str): Type of event (question, confusion, hint_used, etc.)
            student_id (str): Student ID
            data (dict): Event data
        """
        if not self.validate_params(params, ['event_type', 'student_id']):
            raise ValueError("Missing required parameters: event_type, student_id")
        
        event_type = params['event_type']
        student_id = params['student_id']
        data = params.get('data', {})
        
        # Log different types of events
        if event_type == "question":
            self.professor_service.log_question(
                student_id=student_id,
                question=data.get('question', ''),
                artifact=data.get('artifact'),
                section=data.get('section'),
                confidence=data.get('confidence', 1.0),
                response=data.get('response', '')
            )
        
        elif event_type == "confusion":
            self.professor_service.log_confusion_signal(
                student_id=student_id,
                artifact=data.get('artifact', ''),
                section=data.get('section'),
                question=data.get('question', ''),
                signal_type=data.get('signal_type', 'stuck')
            )
        
        return {"success": True, "event_type": event_type}
