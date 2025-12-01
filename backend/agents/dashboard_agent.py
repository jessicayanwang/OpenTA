"""
Dashboard Agent
Handles dashboard metrics, confusion heatmap, and student analytics
"""
from typing import Dict, Any
from datetime import datetime, timedelta

from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse


class DashboardAgent(BaseAgent):
    """
    Specialized agent for dashboard metrics, confusion heatmap, and student analytics
    """
    
    def __init__(self, professor_service):
        super().__init__(
            agent_id="dashboard_agent",
            name="Dashboard Agent",
            capabilities=[
                AgentCapability.VIEW_DASHBOARD,
                AgentCapability.VIEW_CONFUSION_HEATMAP,
                AgentCapability.ANALYZE_STUDENTS,
                AgentCapability.IDENTIFY_CONTENT_GAPS
            ]
        )
        self.professor_service = professor_service
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process a dashboard request
        """
        try:
            content = message.content
            action = content.get('action', 'get_metrics')
            course_id = content.get('course_id', 'cs50')
            
            self.log(f"Processing dashboard action: {action}")
            
            if action == 'get_metrics':
                return await self._get_dashboard_metrics(content, course_id)
            elif action == 'get_confusion_heatmap':
                return await self._get_confusion_heatmap(content, course_id)
            elif action == 'get_student_analytics':
                return await self._get_student_analytics(course_id)
            elif action == 'get_content_gaps':
                return await self._get_content_gaps(course_id)
            elif action == 'log_confusion_signal':
                return await self._log_confusion_signal(content)
            else:
                return self.create_response(
                    success=False,
                    data={},
                    error=f"Unknown action: {action}",
                    confidence=0.0
                )
                
        except Exception as e:
            self.log(f"Error processing dashboard request: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    async def _get_dashboard_metrics(self, content: Dict[str, Any], course_id: str) -> AgentResponse:
        """Get dashboard overview metrics"""
        from database import QuestionLogDB
        days = content.get('days', 7)
        cutoff = datetime.now() - timedelta(days=days)
        
        session = self.professor_service.db.get_session()
        try:
            # Get recent questions from database
            recent_questions = session.query(QuestionLogDB).filter(
                QuestionLogDB.timestamp >= cutoff
            ).all()
            
            # Calculate metrics
            total_questions = len(recent_questions)
            avg_confidence = (
                sum(q.confidence for q in recent_questions) / max(len(recent_questions), 1)
            )
            
            # Count struggling students (3+ confusion signals)
            student_confusion_count = {}
            for signal in self.professor_service.confusion_signals:
                if signal.timestamp >= cutoff:
                    student_id = signal.student_id
                    student_confusion_count[student_id] = student_confusion_count.get(student_id, 0) + 1
            
            struggling_students = len([
                s for s, count in student_confusion_count.items() if count >= 3
            ])
            
            # Unresolved count
            unresolved_count = len([
                item for item in self.professor_service.unresolved_queue.values() 
                if not item.resolved
            ])
            
            # Top confusion topics
            topic_confusion = {}
            for signal in self.professor_service.confusion_signals:
                if signal.timestamp >= cutoff:
                    topic = signal.section or signal.artifact
                    topic_confusion[topic] = topic_confusion.get(topic, 0) + 1
            
            top_topics = sorted(topic_confusion.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Recent activity (last 10 questions)
            recent_activity = sorted(
                recent_questions, key=lambda x: x.timestamp, reverse=True
            )[:10]
            
            return self.create_response(
                success=True,
                data={
                    'metrics': {
                        'total_questions': total_questions,
                        'avg_confidence': round(avg_confidence, 2),
                        'struggling_students': struggling_students,
                        'unresolved_items': unresolved_count
                    },
                    'top_confusion_topics': [
                        {'topic': topic, 'count': count} for topic, count in top_topics
                    ],
                    'recent_activity': [
                        {
                            'question': q.question,
                            'student_id': q.student_id,
                            'confidence': q.confidence,
                            'timestamp': q.timestamp.isoformat(),
                            'artifact': q.artifact or "Unknown"
                        }
                        for q in recent_activity
                    ]
                },
                confidence=1.0,
                reasoning=f"Calculated dashboard metrics for last {days} days"
            )
        finally:
            session.close()
    
    async def _get_confusion_heatmap(self, content: Dict[str, Any], course_id: str) -> AgentResponse:
        """Get confusion heatmap"""
        days = content.get('days', 7)
        
        heatmap = self.professor_service.get_confusion_heatmap(course_id, days)
        
        return self.create_response(
            success=True,
            data={
                'heatmap': [entry.model_dump() for entry in heatmap],
                'total_entries': len(heatmap)
            },
            confidence=1.0,
            reasoning=f"Generated confusion heatmap for last {days} days"
        )
    
    async def _get_student_analytics(self, course_id: str) -> AgentResponse:
        """Get student analytics"""
        from database import QuestionLogDB
        session = self.professor_service.db.get_session()
        try:
            students = {}
            
            # Get all question logs from database
            question_logs = session.query(QuestionLogDB).all()
            
            # Collect data per student
            for q in question_logs:
                student_id = q.student_id
                if student_id not in students:
                    students[student_id] = {
                        "student_id": student_id,
                        "questions_asked": 0,
                        "avg_confidence": 0,
                        "confusion_signals": 0,
                        "last_active": None,
                        "topics": set()
                    }
                
                students[student_id]["questions_asked"] += 1
                students[student_id]["topics"].add(q.section or "Unknown")
                
                if (students[student_id]["last_active"] is None or 
                    q.timestamp > students[student_id]["last_active"]):
                    students[student_id]["last_active"] = q.timestamp
            
            # Count confusion signals
            for signal in self.professor_service.confusion_signals:
                student_id = signal.student_id
                if student_id in students:
                    students[student_id]["confusion_signals"] += 1
            
            # Calculate avg confidence
            for student_id in students:
                student_questions = [
                    q for q in question_logs 
                    if q.student_id == student_id
                ]
                if student_questions:
                    students[student_id]["avg_confidence"] = (
                        sum(q.confidence for q in student_questions) / len(student_questions)
                    )
        
            # Categorize students
            for student in students.values():
                student["topics"] = list(student["topics"])
                student["last_active"] = (
                    student["last_active"].isoformat() if student["last_active"] else None
                )
                
                # Determine status
                if student["confusion_signals"] >= 3:
                    student["status"] = "struggling"
                elif student["questions_asked"] == 0:
                    student["status"] = "silent"
                elif student["avg_confidence"] > 0.8:
                    student["status"] = "thriving"
                else:
                    student["status"] = "active"
            
            return self.create_response(
                success=True,
                data={
                    'students': list(students.values()),
                    'total_count': len(students)
                },
                confidence=1.0,
                reasoning=f"Analyzed {len(students)} students"
            )
        finally:
            session.close()
    
    async def _get_content_gaps(self, course_id: str) -> AgentResponse:
        """Identify content gaps"""
        # Import here to avoid circular dependency
        from mock_data_generator import MockDataGenerator
        
        generator = MockDataGenerator(self.professor_service)
        gaps = generator.generate_content_gaps()
        
        return self.create_response(
            success=True,
            data={
                'gaps': gaps,
                'total_count': len(gaps)
            },
            confidence=0.8,
            reasoning="Identified content gaps from student interactions"
        )
    
    async def _log_confusion_signal(self, content: Dict[str, Any]) -> AgentResponse:
        """Log a confusion signal"""
        student_id = content.get('student_id', 'unknown')
        artifact = content.get('artifact', '')
        section = content.get('section')
        question = content.get('question', '')
        signal_type = content.get('signal_type', 'stuck')
        
        self.professor_service.log_confusion_signal(
            student_id=student_id,
            artifact=artifact,
            section=section,
            question=question,
            signal_type=signal_type
        )
        
        return self.create_response(
            success=True,
            data={'logged': True},
            confidence=1.0,
            reasoning="Confusion signal logged"
        )
