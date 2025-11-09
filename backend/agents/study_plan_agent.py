"""
Study Plan Agent - Refactored for Multi-Agent Framework
Generates personalized study plans
"""
import uuid
from .base_agent import BaseAgent, AgentCapability
from protocols.agent_message import AgentMessage, AgentResponse
from models import StudyPlanResponse, WeekPlan, StudyTask

class StudyPlanAgent(BaseAgent):
    """
    Specialized agent for generating personalized study plans
    """
    
    def __init__(self):
        super().__init__(
            agent_id="study_plan_agent",
            name="Study Plan Agent",
            capabilities=[AgentCapability.GENERATE_STUDY_PLANS]
        )
    
    async def process(self, message: AgentMessage) -> AgentResponse:
        """
        Process a study plan request
        """
        try:
            content = message.content
            student_id = content.get('student_id', 'unknown')
            
            # Extract study plan parameters
            goal_scope = content.get('goal_scope', 'term')
            hours_per_week = content.get('hours_per_week', 10)
            current_level = content.get('current_level', 'beginner')
            duration_weeks = content.get('duration_weeks')
            exam_in_weeks = content.get('exam_in_weeks')
            focus_topics = content.get('focus_topics', [])
            constraints = content.get('constraints', [])
            
            self.log(f"Generating study plan: {goal_scope}, {hours_per_week}hrs/week, level: {current_level}")
            
            # Get student profile
            student_profile = self.memory.get_or_create_student_profile(student_id)
            
            # Generate plan based on scope
            if goal_scope == 'term':
                plan = self._generate_term_plan(
                    hours_per_week, current_level, duration_weeks or 14, focus_topics, constraints
                )
            elif goal_scope == 'midterm':
                plan = self._generate_exam_plan(
                    hours_per_week, current_level, exam_in_weeks or 4, 'midterm', focus_topics
                )
            elif goal_scope == 'final':
                plan = self._generate_exam_plan(
                    hours_per_week, current_level, exam_in_weeks or 6, 'final', focus_topics
                )
            else:
                plan = self._generate_term_plan(hours_per_week, current_level, 14, focus_topics, constraints)
            
            # Update student profile
            student_profile.study_plan_progress = {
                'plan_created': True,
                'goal_scope': goal_scope,
                'weeks': len(plan.weekly_plan)
            }
            
            return self.create_response(
                success=True,
                data={'study_plan': plan.dict()},
                confidence=0.9,
                reasoning=f"Generated {goal_scope} study plan with {len(plan.weekly_plan)} weeks"
            )
            
        except Exception as e:
            self.log(f"Error generating study plan: {str(e)}", "ERROR")
            return self.create_response(
                success=False,
                data={},
                error=str(e),
                confidence=0.0
            )
    
    def _generate_term_plan(self, hours_per_week, level, duration_weeks, focus_topics, constraints):
        """Generate a full-term study plan"""
        weekly_plans = []
        
        # CS50 typical curriculum
        topics_by_week = [
            ("Week 1-2", ["C Basics", "Variables", "Conditionals", "Loops"], ["Problem Set 1"]),
            ("Week 3-4", ["Arrays", "Strings", "Command-line Arguments"], ["Problem Set 2"]),
            ("Week 5-6", ["Algorithms", "Sorting", "Searching", "Big O"], ["Problem Set 3"]),
            ("Week 7-8", ["Memory", "Pointers", "Dynamic Allocation"], ["Problem Set 4"]),
            ("Week 9-10", ["Data Structures", "Linked Lists", "Hash Tables"], ["Problem Set 5"]),
            ("Week 11-12", ["Python Basics", "File I/O", "Libraries"], ["Problem Set 6"]),
            ("Week 13-14", ["SQL", "Databases", "Web Programming"], ["Final Project"])
        ]
        
        for i, (week_range, topics, resources) in enumerate(topics_by_week[:duration_weeks//2]):
            week_num = i * 2 + 1
            
            # Adjust based on level
            study_hours = hours_per_week
            if level == "beginner":
                study_hours = min(hours_per_week, 12)
            elif level == "advanced":
                study_hours = min(hours_per_week, 8)
            
            # Create tasks for the week
            tasks = self._create_weekly_tasks(topics, resources, study_hours, constraints)
            
            weekly_plans.append(WeekPlan(
                week_number=week_num,
                objectives=topics,
                tasks=tasks
            ))
        
        title = f"CS50 {duration_weeks}-Week Study Plan"
        summary = f"A structured {duration_weeks}-week plan covering C programming, algorithms, data structures, and web development."
        
        tips = self._generate_study_tips(level, constraints)
        
        return StudyPlanResponse(
            title=title,
            summary=summary,
            hours_per_week=hours_per_week,
            duration_weeks=duration_weeks,
            weekly_plan=weekly_plans,
            tips=tips
        )
    
    def _generate_exam_plan(self, hours_per_week, level, weeks_until_exam, exam_type, focus_topics):
        """Generate an exam preparation plan"""
        weekly_plans = []
        
        if exam_type == 'midterm':
            review_topics = ["C Basics", "Arrays", "Algorithms", "Memory Management"]
        else:  # final
            review_topics = ["All C Concepts", "Data Structures", "Python", "SQL", "Web Programming"]
        
        # Distribute topics across weeks
        topics_per_week = len(review_topics) // max(weeks_until_exam - 1, 1)
        
        for week in range(1, weeks_until_exam + 1):
            if week == weeks_until_exam:
                # Final week: practice and review
                objectives = ["Practice Problems", "Review Weak Areas", "Mock Exam"]
                tasks = [
                    StudyTask(day="Monday-Wednesday", focus="Practice problems", duration_hours=hours_per_week * 0.6),
                    StudyTask(day="Thursday-Friday", focus="Review mistakes", duration_hours=hours_per_week * 0.3),
                    StudyTask(day="Weekend", focus="Light review and rest", duration_hours=hours_per_week * 0.1)
                ]
            else:
                # Regular review weeks
                start_idx = (week - 1) * topics_per_week
                end_idx = start_idx + topics_per_week
                objectives = review_topics[start_idx:end_idx] if start_idx < len(review_topics) else review_topics[-2:]
                
                tasks = self._create_weekly_tasks(objectives, [], hours_per_week, [])
            
            weekly_plans.append(WeekPlan(
                week_number=week,
                objectives=objectives,
                tasks=tasks
            ))
        
        title = f"CS50 {exam_type.capitalize()} Exam Prep ({weeks_until_exam} weeks)"
        summary = f"Focused {weeks_until_exam}-week plan to prepare for the {exam_type} exam."
        
        tips = [
            "Focus on understanding concepts, not just memorizing",
            "Practice coding by hand",
            "Review past problem sets",
            "Get enough sleep before the exam"
        ]
        
        return StudyPlanResponse(
            title=title,
            summary=summary,
            hours_per_week=hours_per_week,
            duration_weeks=weeks_until_exam,
            weekly_plan=weekly_plans,
            tips=tips
        )
    
    def _create_weekly_tasks(self, topics, resources, hours, constraints):
        """Create study tasks for a week"""
        tasks = []
        
        # Distribute hours across the week
        weekday_hours = hours * 0.6
        weekend_hours = hours * 0.4
        
        # Check constraints
        no_weekends = "no weekends" in [c.lower() for c in constraints]
        only_evenings = "only evenings" in [c.lower() for c in constraints]
        
        if no_weekends:
            weekday_hours = hours
            weekend_hours = 0
        
        # Weekday tasks
        if weekday_hours > 0:
            time_note = " (evenings)" if only_evenings else ""
            tasks.append(StudyTask(
                day=f"Monday-Friday{time_note}",
                focus=f"Learn: {', '.join(topics[:2])}",
                duration_hours=weekday_hours * 0.5,
                resources=resources[:2] if resources else None
            ))
            tasks.append(StudyTask(
                day=f"Wednesday-Thursday{time_note}",
                focus="Practice problems and exercises",
                duration_hours=weekday_hours * 0.5,
                resources=["Practice problems", "Code exercises"]
            ))
        
        # Weekend tasks
        if weekend_hours > 0:
            tasks.append(StudyTask(
                day="Weekend",
                focus=f"Review and work on {resources[0] if resources else 'assignments'}",
                duration_hours=weekend_hours,
                resources=resources if resources else None
            ))
        
        return tasks
    
    def _generate_study_tips(self, level, constraints):
        """Generate personalized study tips"""
        tips = [
            "Break study sessions into 25-minute focused blocks (Pomodoro technique)",
            "Code along with lectures - don't just watch",
            "Start problem sets early to have time for questions",
            "Join study groups or find a study partner"
        ]
        
        if level == "beginner":
            tips.append("Don't worry if things seem hard at first - programming takes practice!")
            tips.append("Focus on understanding fundamentals before moving to advanced topics")
        elif level == "advanced":
            tips.append("Challenge yourself with additional exercises beyond the problem sets")
            tips.append("Help others - teaching reinforces your own understanding")
        
        if "no weekends" in [c.lower() for c in constraints]:
            tips.append("Since you're studying on weekdays only, stay consistent with your schedule")
        
        return tips
