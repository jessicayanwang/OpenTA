'use client'

import { useState } from 'react'

type StudyTask = {
  day: string
  focus: string
  duration_hours: number
  resources?: string[]
}

type WeekPlan = {
  week_number: number
  objectives: string[]
  tasks: StudyTask[]
}

type StudyPlanResponse = {
  title: string
  summary: string
  hours_per_week: number
  duration_weeks: number
  weekly_plan: WeekPlan[]
  tips: string[]
}

const constraintOptions = [
  'no weekends',
  'only weekends',
  'only evenings',
]

export default function StudyPlanPage() {
  const [goalScope, setGoalScope] = useState<'term' | 'midterm' | 'final'>('term')
  const [hoursPerWeek, setHoursPerWeek] = useState<number>(8)
  const [currentLevel, setCurrentLevel] = useState<'beginner' | 'intermediate' | 'advanced'>('intermediate')
  const [durationWeeks, setDurationWeeks] = useState<number>(12)
  const [examInWeeks, setExamInWeeks] = useState<number>(4)
  const [focusTopics, setFocusTopics] = useState<string>('')
  const [constraints, setConstraints] = useState<string[]>([])
  const [notes, setNotes] = useState<string>('')

  const [loading, setLoading] = useState(false)
  const [plan, setPlan] = useState<StudyPlanResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const toggleConstraint = (c: string) => {
    setConstraints((prev: string[]) => prev.includes(c) ? prev.filter((x: string) => x !== c) : [...prev, c])
  }

  const submit = async () => {
    setLoading(true)
    setError(null)
    setPlan(null)

    const body: any = {
      course_id: 'cs50',
      goal_scope: goalScope,
      hours_per_week: hoursPerWeek,
      current_level: currentLevel,
      focus_topics: focusTopics.split(',').map((s: string) => s.trim()).filter(Boolean),
      constraints,
      notes: notes || undefined,
    }

    if (goalScope === 'term') {
      body.duration_weeks = durationWeeks
    } else {
      body.exam_in_weeks = examInWeeks
    }

    try {
      const res = await fetch('http://localhost:8000/api/study-plan', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      })
      if (!res.ok) throw new Error('Failed to generate plan')
      const data: StudyPlanResponse = await res.json()
      setPlan(data)
    } catch (e: any) {
      setError(e?.message || 'Something went wrong')
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">🗓️ Study Plan Generator</h1>
          <p className="text-gray-600">Create a personalized plan based on your goals, schedule, and current level.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Form */}
          <div className="bg-white rounded-lg shadow-lg p-6 lg:col-span-1 space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Goal scope</label>
              <select
                value={goalScope}
                onChange={e => setGoalScope(e.target.value as any)}
                className="w-full border rounded p-2"
              >
                <option value="term">Term plan</option>
                <option value="midterm">Midterm prep</option>
                <option value="final">Final prep</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Current level</label>
              <select
                value={currentLevel}
                onChange={e => setCurrentLevel(e.target.value as any)}
                className="w-full border rounded p-2"
              >
                <option value="beginner">Beginner</option>
                <option value="intermediate">Intermediate</option>
                <option value="advanced">Advanced</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Hours per week</label>
              <input
                type="number"
                min={1}
                max={40}
                value={hoursPerWeek}
                onChange={e => setHoursPerWeek(parseInt(e.target.value || '0'))}
                className="w-full border rounded p-2"
              />
            </div>

            {goalScope === 'term' ? (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Duration (weeks)</label>
                <input
                  type="number"
                  min={1}
                  max={24}
                  value={durationWeeks}
                  onChange={e => setDurationWeeks(parseInt(e.target.value || '0'))}
                  className="w-full border rounded p-2"
                />
              </div>
            ) : (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Exam in (weeks)</label>
                <input
                  type="number"
                  min={1}
                  max={12}
                  value={examInWeeks}
                  onChange={e => setExamInWeeks(parseInt(e.target.value || '0'))}
                  className="w-full border rounded p-2"
                />
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Focus topics (comma-separated)</label>
              <input
                type="text"
                placeholder="e.g., Arrays, Loops, Pointers"
                value={focusTopics}
                onChange={e => setFocusTopics(e.target.value)}
                className="w-full border rounded p-2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Constraints</label>
              <div className="flex flex-wrap gap-2">
                {constraintOptions.map(c => (
                  <button
                    key={c}
                    onClick={() => toggleConstraint(c)}
                    className={`px-3 py-1 rounded-full text-sm border ${constraints.includes(c) ? 'bg-indigo-600 text-white border-indigo-600' : 'bg-white text-gray-700 border-gray-300'}`}
                  >
                    {c}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Notes (optional)</label>
              <textarea
                rows={3}
                value={notes}
                onChange={e => setNotes(e.target.value)}
                placeholder="Anything else you want the plan to consider"
                className="w-full border rounded p-2"
              />
            </div>

            <button
              onClick={submit}
              disabled={loading}
              className="w-full py-3 bg-indigo-600 text-white rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400"
            >
              {loading ? 'Generating...' : 'Generate Plan'}
            </button>

            {error && (
              <div className="mt-3 text-sm text-red-600">{error}</div>
            )}
          </div>

          {/* Output */}
          <div className="bg-white rounded-lg shadow-lg p-6 lg:col-span-2">
            {!plan && !loading && (
              <div className="text-gray-600">Fill the form and click Generate to see your plan here.</div>
            )}

            {plan && (
              <div className="space-y-6">
                <div>
                  <div className="text-2xl font-bold text-indigo-900">{plan.title}</div>
                  <div className="text-gray-600 mt-1">{plan.summary}</div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {plan.tips.map((tip, i) => (
                    <div key={i} className="bg-indigo-50 border-l-4 border-indigo-400 p-3 rounded text-sm text-indigo-900">
                      {tip}
                    </div>
                  ))}
                </div>

                <div className="space-y-4">
                  {plan.weekly_plan.map(week => (
                    <div key={week.week_number} className="border rounded-lg p-4">
                      <div className="font-semibold text-indigo-800 mb-2">Week {week.week_number}</div>
                      <div className="text-sm text-gray-700 mb-2">
                        Objectives: {week.objectives.join('; ')}
                      </div>
                      <div className="space-y-2">
                        {week.tasks.map((task, idx) => (
                          <div key={idx} className="bg-gray-50 p-3 rounded border text-sm">
                            <div className="font-medium text-gray-800">{task.day} • {task.duration_hours}h</div>
                            <div className="text-gray-700">{task.focus}</div>
                            {task.resources && task.resources.length > 0 && (
                              <div className="text-xs text-gray-600 mt-1">Resources: {task.resources.join(', ')}</div>
                            )}
                          </div>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {loading && (
              <div className="text-gray-700">Generating your plan...</div>
            )}
          </div>
        </div>
      </div>
    </main>
  )
}
