"""
Rule-based Study Plan Agent
Generates a personalized study plan based on user inputs without external LLM dependencies.
"""
from typing import List, Optional
from datetime import datetime, timedelta

from models import (
    StudyPlanRequest,
    StudyPlanResponse,
    WeekPlan,
    StudyTask,
)

WEEK_DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

class StudyPlanAgent:
    """Generates a weekly study plan using simple heuristics"""

    def __init__(self):
        pass

    def generate_plan(self, req: StudyPlanRequest) -> StudyPlanResponse:
        # Determine duration in weeks
        duration_weeks = self._determine_duration_weeks(req)

        # Determine focus topics; provide defaults per level if none
        focus_topics = req.focus_topics or self._default_focus_topics(req.current_level)

        # Compute weekly objectives progression (spiral review and increasing depth)
        weekly_objectives = self._build_weekly_objectives(focus_topics, duration_weeks, req.goal_scope)

        # Build tasks distribution per week
        weekly_plan: List[WeekPlan] = []
        for w in range(1, duration_weeks + 1):
            tasks = self._build_tasks_for_week(
                hours=req.hours_per_week,
                constraints=req.constraints or [],
                focus_topics=weekly_objectives[w-1],
                current_level=req.current_level,
                goal_scope=req.goal_scope,
                week_number=w,
                total_weeks=duration_weeks,
            )
            weekly_plan.append(
                WeekPlan(
                    week_number=w,
                    objectives=weekly_objectives[w-1],
                    tasks=tasks,
                )
            )

        title = self._build_title(req, duration_weeks)
        summary = self._build_summary(req, duration_weeks, focus_topics)
        tips = self._build_tips(req)

        return StudyPlanResponse(
            title=title,
            summary=summary,
            hours_per_week=req.hours_per_week,
            duration_weeks=duration_weeks,
            weekly_plan=weekly_plan,
            tips=tips,
        )

    def _determine_duration_weeks(self, req: StudyPlanRequest) -> int:
        if req.goal_scope.lower() == "term":
            return req.duration_weeks or 12
        # Exam-focused
        if req.exam_in_weeks and req.exam_in_weeks > 0:
            return min(max(req.exam_in_weeks, 1), 12)
        return req.duration_weeks or 4

    def _default_focus_topics(self, level: str) -> List[str]:
        lvl = level.lower()
        if "beginner" in lvl:
            return [
                "Foundations",
                "Syntax & Basics",
                "Control Flow",
                "Functions",
                "Data Structures",
                "Problem Solving",
            ]
        if "advanced" in lvl:
            return [
                "Optimization",
                "Advanced Data Structures",
                "Algorithms & Complexity",
                "Testing & Debugging",
                "Systems & Performance",
                "Project Work",
            ]
        return [
            "Core Concepts",
            "Data Types & Structures",
            "Algorithmic Thinking",
            "Debugging",
            "Applications",
            "Review",
        ]

    def _build_weekly_objectives(self, focus_topics: List[str], duration_weeks: int, scope: str) -> List[List[str]]:
        objs: List[List[str]] = []
        # Rotate through topics; increase emphasis near exams
        exam_push_weeks = 2 if scope.lower() in ("midterm", "final") else 0
        for w in range(duration_weeks):
            # pick 2 topics rotating
            primary = focus_topics[w % len(focus_topics)]
            secondary = focus_topics[(w + 1) % len(focus_topics)]
            objectives = [f"Master: {primary}", f"Reinforce: {secondary}"]
            if exam_push_weeks and w >= duration_weeks - exam_push_weeks:
                objectives.append("Targeted practice on past exams and weak areas")
            objs.append(objectives)
        return objs

    def _build_tasks_for_week(
        self,
        hours: int,
        constraints: List[str],
        focus_topics: List[str],
        current_level: str,
        goal_scope: str,
        week_number: int,
        total_weeks: int,
    ) -> List[StudyTask]:
        # Distribute hours across 4-6 sessions depending on constraints
        available_days = self._available_days(constraints)
        sessions = min(max(len(available_days) - (2 if "no weekends" in [c.lower() for c in constraints] else 1), 4), 6)
        session_hours = round(hours / sessions, 1) if sessions else hours

        tasks: List[StudyTask] = []
        # Map objectives to sessions: learn, practice, review
        modes = self._session_modes(goal_scope, current_level, week_number, total_weeks)

        for i in range(sessions):
            day = available_days[i % len(available_days)]
            mode = modes[i % len(modes)]
            focus = f"{mode}: {focus_topics[0].replace('Master: ', '').replace('Reinforce: ', '')}"
            resources = self._suggest_resources(mode)
            tasks.append(
                StudyTask(
                    day=day,
                    focus=focus,
                    duration_hours=session_hours,
                    resources=resources,
                )
            )

        return tasks

    def _available_days(self, constraints: List[str]) -> List[str]:
        cl = [c.lower() for c in constraints]
        days = WEEK_DAYS.copy()
        if "no weekends" in cl:
            days = days[:5]
        if "only weekends" in cl:
            days = days[5:]
        if "only evenings" in cl:
            # heuristic: skip Monday/Friday to avoid burnout
            days = [d for d in days if d not in ("Monday", "Friday")] or days
        return days or WEEK_DAYS

    def _session_modes(self, goal_scope: str, current_level: str, week_number: int, total_weeks: int) -> List[str]:
        scope = goal_scope.lower()
        lvl = current_level.lower()
        if scope in ("midterm", "final") and week_number > total_weeks - 2:
            return ["Timed Practice", "Review", "Error Log"]
        if "beginner" in lvl:
            return ["Learn", "Practice", "Review"]
        return ["Practice", "Learn", "Review"]

    def _suggest_resources(self, mode: str) -> List[str]:
        if mode == "Learn":
            return [
                "Course notes section",
                "Lecture video",
                "Official docs/tutorial",
            ]
        if mode == "Practice":
            return [
                "Problem set questions",
                "Practice problems",
                "Coding exercises (LeetCode-style if applicable)",
            ]
        if mode == "Timed Practice":
            return [
                "Past exam questions",
                "Timing yourself (Pomodoro 25/5)",
            ]
        if mode == "Error Log":
            return [
                "Maintain mistakes log",
                "Rework incorrect problems",
            ]
        return ["Review notes", "Flashcards"]

    def _build_title(self, req: StudyPlanRequest, duration_weeks: int) -> str:
        scope = req.goal_scope.capitalize()
        return f"{scope} Study Plan for {req.course_id.upper()} ({duration_weeks} weeks)"

    def _build_summary(self, req: StudyPlanRequest, duration_weeks: int, focus_topics: List[str]) -> str:
        scope = req.goal_scope
        details = []
        if scope.lower() == "term":
            details.append(f"Duration: {duration_weeks} weeks")
        elif req.exam_in_weeks:
            details.append(f"Exam in {req.exam_in_weeks} weeks")
        details.append(f"Hours/week: {req.hours_per_week}")
        details.append(f"Level: {req.current_level}")
        if req.constraints:
            details.append(f"Constraints: {', '.join(req.constraints)}")
        if req.notes:
            details.append(f"Notes: {req.notes}")
        return " | ".join(details)

    def _build_tips(self, req: StudyPlanRequest) -> List[str]:
        tips = [
            "Use a consistent study schedule and protect your study blocks.",
            "Track weak areas and revisit them weekly.",
            "Do spaced repetition on key concepts.",
            "Simulate test conditions for exam prep weeks.",
        ]
        if req.goal_scope.lower() in ("midterm", "final"):
            tips.append("Do at least two timed practice sessions each week before the exam.")
        if req.hours_per_week >= 12:
            tips.append("Batch similar tasks to reduce context switching.")
        return tips
