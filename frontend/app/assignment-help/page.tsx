'use client'

import { useState } from 'react'
import Link from 'next/link'

interface Citation {
  source: string
  section: string
  text: string
  relevance_score: number
}

interface AssignmentHelpResponse {
  guidance: string
  concepts: string[]
  resources: string[]
  next_steps: string[]
  citations: Citation[]
}

// Mock data for demonstration
const MOCK_RESPONSES: { [key: string]: AssignmentHelpResponse } = {
  'getting_started': {
    guidance: `🎯 **Great question! Let's break this down step by step.**

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

Remember: Programming is about problem-solving first, coding second! 🧠`,
    concepts: [
      'Problem decomposition',
      'Input/Output analysis',
      'Requirements gathering',
      'Algorithm design basics'
    ],
    resources: [
      'Review the problem requirements carefully',
      'Look at the example outputs provided',
      'Check lecture notes on program structure',
      'Review shorts on the relevant topic'
    ],
    next_steps: [
      'Write out the problem in your own words',
      'List all inputs and expected outputs',
      'Sketch out the main steps in pseudocode',
      'Only then start writing actual code'
    ],
    citations: [
      {
        source: 'cs50_assignment1.txt',
        section: 'Problem 2: Mario',
        text: 'Implement a program that prints a half-pyramid of a specified height using hashes (#). Requirements: Prompt user for height (between 1 and 8, inclusive). If invalid input, re-prompt. Print right-aligned pyramid.',
        relevance_score: 0.92
      }
    ]
  },
  'debugging': {
    guidance: `🐛 **Debugging is a crucial skill! Let's troubleshoot systematically.**

**Debugging Strategy:**

1. **Understand the error:**
   - What error message are you seeing? (Read it carefully!)
   - At what line does it occur?
   - What were you trying to do at that point?

2. **Use debugging tools:**
   - Add printf statements to check variable values
   - Use the debugger to step through code line by line
   - Check boundary cases (what if input is 0? negative? very large?)

3. **Common issues to check:**
   - Are your variables initialized?
   - Are you using the right operators (= vs ==)?
   - Are your loop conditions correct?
   - Are you checking for the right conditions?

**Think about:** What did you expect to happen vs. what actually happened?`,
    concepts: [
      'Debugging techniques',
      'Reading error messages',
      'Variable tracking',
      'Edge case testing'
    ],
    resources: [
      'Use check50 to test your code',
      'Review debugging tips in lecture notes',
      'Use printf debugging or debugger50',
      'Post on Ed Discussion (describe what you tried)'
    ],
    next_steps: [
      'Identify the exact line where the problem occurs',
      'Print out variable values before that line',
      'Test with simple inputs first',
      'Check if your logic handles all cases'
    ],
    citations: [
      {
        source: 'cs50_assignment1.txt',
        section: 'Getting Help',
        text: 'If you\'re stuck: 1. Review lecture notes and shorts 2. Post on Ed Discussion (no code sharing!) 3. Attend office hours 4. Use the debugger to step through your code',
        relevance_score: 0.88
      }
    ]
  },
  'algorithm': {
    guidance: `💡 **Let's think about the algorithm logically!**

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

Remember: A good algorithm is clear and handles all cases! 📝`,
    concepts: [
      'Algorithm design',
      'Control flow (loops, conditionals)',
      'Step-by-step problem solving',
      'Pattern recognition'
    ],
    resources: [
      'Review relevant lecture examples',
      'Look at similar problems from class',
      'Check shorts on loops and conditionals',
      'Draw flowcharts if helpful'
    ],
    next_steps: [
      'Write pseudocode for your approach',
      'Trace through your logic with sample inputs',
      'Identify patterns in the problem',
      'Start with the simplest version, then add complexity'
    ],
    citations: [
      {
        source: 'cs50_assignment1.txt',
        section: 'Problem 2: Mario',
        text: 'Example output for height 4:\n   #\n  ##\n ###\n####',
        relevance_score: 0.85
      }
    ]
  },
  'implementation': {
    guidance: `⌨️ **Let's work on the implementation!**

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

Remember: Small steps lead to big solutions! 🪜`,
    concepts: [
      'C syntax and semantics',
      'Variable types and declarations',
      'Function structure',
      'Incremental development'
    ],
    resources: [
      'Review lecture code examples',
      'Check CS50 manual pages (man50)',
      'Look at shorts on C syntax',
      'Compile frequently with make'
    ],
    next_steps: [
      'Start with a basic skeleton that compiles',
      'Add one feature at a time',
      'Test with check50 after each major change',
      'Read compiler error messages carefully'
    ],
    citations: [
      {
        source: 'cs50_assignment1.txt',
        section: 'Getting Started',
        text: '1. Log into CS50 IDE 2. Run update50 to update your IDE 3. Create a directory called pset1 4. Navigate to that directory',
        relevance_score: 0.80
      }
    ]
  }
}

const PROBLEMS = [
  { id: 'problem1', name: 'Problem 1: Hello' },
  { id: 'problem2', name: 'Problem 2: Mario' },
  { id: 'problem3', name: 'Problem 3: Credit' },
]

const HINT_SUGGESTIONS = [
  { label: '🚀 How do I start?', type: 'getting_started' },
  { label: '🐛 My code has an error', type: 'debugging' },
  { label: '💭 What algorithm should I use?', type: 'algorithm' },
  { label: '⌨️ How do I implement this?', type: 'implementation' },
]

export default function AssignmentHelpPage() {
  const [selectedProblem, setSelectedProblem] = useState<string>('problem2')
  const [question, setQuestion] = useState<string>('')
  const [context, setContext] = useState<string>('')
  const [loading, setLoading] = useState<boolean>(false)
  const [response, setResponse] = useState<AssignmentHelpResponse | null>(null)
  const [useMockData, setUseMockData] = useState<boolean>(true)

  const handleSubmit = async () => {
    if (!question.trim()) return

    setLoading(true)
    setResponse(null)

    try {
      if (useMockData) {
        // Use mock data for demonstration
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        const questionLower = question.toLowerCase()
        let mockType = 'getting_started'
        
        if (questionLower.includes('error') || questionLower.includes('bug') || questionLower.includes('wrong')) {
          mockType = 'debugging'
        } else if (questionLower.includes('algorithm') || questionLower.includes('approach') || questionLower.includes('solve')) {
          mockType = 'algorithm'
        } else if (questionLower.includes('code') || questionLower.includes('write') || questionLower.includes('implement')) {
          mockType = 'implementation'
        }
        
        setResponse(MOCK_RESPONSES[mockType])
      } else {
        // Real API call
        const res = await fetch('http://localhost:8000/api/assignment-help', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question,
            problem_number: PROBLEMS.find(p => p.id === selectedProblem)?.name,
            context: context || undefined,
            course_id: 'cs50'
          }),
        })
        
        if (!res.ok) throw new Error('Failed to get help')
        const data = await res.json()
        setResponse(data)
      }
    } catch (error) {
      console.error('Error:', error)
      alert('Error getting help. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }

  const handleHintClick = (type: string) => {
    const hintText = HINT_SUGGESTIONS.find(h => h.type === type)?.label || ''
    setQuestion(hintText)
    if (useMockData) {
      setLoading(true)
      setTimeout(() => {
        setResponse(MOCK_RESPONSES[type])
        setLoading(false)
      }, 1500)
    }
  }

  return (
    <main className="min-h-screen bg-gradient-to-br from-green-50 to-teal-100">
      <div className="max-w-7xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold text-green-900 mb-2">📝 Assignment Helper</h1>
              <p className="text-gray-600">
                Get guidance on assignments without direct answers. I'll help you learn by asking the right questions!
              </p>
            </div>
            <Link 
              href="/"
              className="px-4 py-2 text-gray-600 hover:text-gray-900 transition"
            >
              ← Back to Chat
            </Link>
          </div>
          
          {/* Mock Data Toggle */}
          <div className="mt-4 flex items-center gap-2 text-sm">
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={useMockData}
                onChange={(e) => setUseMockData(e.target.checked)}
                className="rounded"
              />
              <span className="text-gray-700">
                Use mock data (for demo - uncheck to use real API)
              </span>
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Input Form */}
          <div className="lg:col-span-1 space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Select Problem
                </label>
                <select
                  value={selectedProblem}
                  onChange={(e) => setSelectedProblem(e.target.value)}
                  className="w-full border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                >
                  {PROBLEMS.map(problem => (
                    <option key={problem.id} value={problem.id}>
                      {problem.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Your Question
                </label>
                <textarea
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder="What do you need help with?"
                  rows={4}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  What have you tried? (optional)
                </label>
                <textarea
                  value={context}
                  onChange={(e) => setContext(e.target.value)}
                  placeholder="Tell me what you've attempted so far..."
                  rows={3}
                  className="w-full border border-gray-300 rounded-lg p-3 focus:ring-2 focus:ring-green-500 focus:border-transparent"
                />
              </div>

              <button
                onClick={handleSubmit}
                disabled={loading || !question.trim()}
                className="w-full py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
              >
                {loading ? 'Getting Guidance...' : 'Get Help'}
              </button>
            </div>

            {/* Quick Hints */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-sm font-semibold text-gray-700 mb-3">
                💡 Quick Hints
              </h3>
              <div className="space-y-2">
                {HINT_SUGGESTIONS.map((hint) => (
                  <button
                    key={hint.type}
                    onClick={() => handleHintClick(hint.type)}
                    className="w-full text-left px-3 py-2 text-sm bg-green-50 hover:bg-green-100 text-green-800 rounded-lg transition"
                  >
                    {hint.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Response Display */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-lg p-6 min-h-[600px]">
              {!response && !loading && (
                <div className="text-center text-gray-500 mt-20">
                  <div className="text-6xl mb-4">🎓</div>
                  <p className="text-lg">Ask a question to get started!</p>
                  <p className="text-sm mt-2">I'll guide you through solving the problem without giving away the answer.</p>
                </div>
              )}

              {loading && (
                <div className="text-center mt-20">
                  <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mb-4"></div>
                  <p className="text-gray-600">Preparing your guidance...</p>
                </div>
              )}

              {response && (
                <div className="space-y-6">
                  {/* Guidance */}
                  <div>
                    <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <span>💡</span>
                      <span>Guidance</span>
                    </h2>
                    <div className="bg-green-50 border-l-4 border-green-500 p-4 rounded-lg">
                      <div className="text-gray-800 whitespace-pre-wrap">
                        {response.guidance}
                      </div>
                    </div>
                  </div>

                  {/* Key Concepts */}
                  <div>
                    <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <span>📚</span>
                      <span>Key Concepts to Review</span>
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {response.concepts.map((concept, idx) => (
                        <div
                          key={idx}
                          className="bg-blue-50 border border-blue-200 px-4 py-2 rounded-lg text-sm text-blue-900"
                        >
                          • {concept}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Resources */}
                  <div>
                    <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <span>📖</span>
                      <span>Recommended Resources</span>
                    </h2>
                    <div className="space-y-2">
                      {response.resources.map((resource, idx) => (
                        <div
                          key={idx}
                          className="bg-purple-50 border-l-4 border-purple-400 px-4 py-2 rounded text-sm text-purple-900"
                        >
                          {resource}
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Next Steps */}
                  <div>
                    <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                      <span>➡️</span>
                      <span>Next Steps</span>
                    </h2>
                    <div className="space-y-2">
                      {response.next_steps.map((step, idx) => (
                        <div
                          key={idx}
                          className="bg-orange-50 border-l-4 border-orange-400 px-4 py-3 rounded text-sm text-orange-900 flex items-start gap-3"
                        >
                          <span className="font-bold text-orange-600">{idx + 1}.</span>
                          <span>{step}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Citations */}
                  {response.citations && response.citations.length > 0 && (
                    <div>
                      <h2 className="text-xl font-bold text-gray-800 mb-3 flex items-center gap-2">
                        <span>📎</span>
                        <span>Relevant Assignment Details</span>
                      </h2>
                      <div className="space-y-3">
                        {response.citations.map((citation, idx) => (
                          <div
                            key={idx}
                            className="bg-gray-50 border border-gray-200 rounded-lg p-4"
                          >
                            <div className="font-semibold text-gray-800 mb-2">
                              {citation.source} - {citation.section}
                            </div>
                            <div className="text-sm text-gray-700 mb-2">
                              {citation.text}
                            </div>
                            <div className="text-xs text-gray-500">
                              Relevance: {(citation.relevance_score * 100).toFixed(0)}%
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  {/* Reminder */}
                  <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg">
                    <p className="text-sm text-yellow-800">
                      <strong>Remember:</strong> The goal is to learn and understand, not just to complete the assignment.
                      Take your time with each step and make sure you understand the concepts!
                    </p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  )
}
