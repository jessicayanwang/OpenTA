# OpenTA Backend

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create `.env` file with your OpenAI API key:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

3. Run the server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

- `POST /api/chat` - Ask a question and get a grounded answer with citations
- `GET /api/health` - Health check endpoint
- `POST /api/study-plan` - Generate a personalized study plan

### Study Plan API

Request body (`StudyPlanRequest`):
```json
{
  "course_id": "cs50",
  "goal_scope": "term | midterm | final",
  "hours_per_week": 8,
  "current_level": "beginner | intermediate | advanced",
  "duration_weeks": 12,              // required for goal_scope = term
  "exam_in_weeks": 4,                // required for goal_scope = midterm/final
  "focus_topics": ["Arrays", "Loops"],
  "constraints": ["no weekends", "only evenings"],
  "notes": "Prefer short sessions"
}
```

Response (`StudyPlanResponse`):
```json
{
  "title": "Term Study Plan for CS50 (12 weeks)",
  "summary": "Duration: 12 weeks | Hours/week: 8 | Level: intermediate",
  "hours_per_week": 8,
  "duration_weeks": 12,
  "weekly_plan": [
    {
      "week_number": 1,
      "objectives": ["Master: Arrays", "Reinforce: Loops"],
      "tasks": [
        { "day": "Monday", "focus": "Learn: Arrays", "duration_hours": 2.0, "resources": ["Course notes section"] }
      ]
    }
  ],
  "tips": ["Use a consistent study schedule and protect your study blocks."]
}
```
