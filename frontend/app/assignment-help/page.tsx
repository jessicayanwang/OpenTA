'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle, HelpCircle, BookOpen, FileText, User } from 'lucide-react'
import Logo from '@/components/Logo'

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

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  userContext?: string
  problemNumber?: string
  response?: AssignmentHelpResponse
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
  'code_review': {
    guidance: `👀 **Let's review your code together!**

When sharing code, I can help you think through:

**Logic Review:**
- Does your code follow the algorithm you planned?
- Are there any logical errors in your conditions?
- Do your loops iterate the correct number of times?

**Common Patterns to Check:**
- Variable initialization
- Loop boundaries (off-by-one errors?)
- Condition logic (&&, ||, !)
- Return values

**Questions to Consider:**
- Have you tested with edge cases?
- Does it work with the smallest valid input?
- What about the largest?
- What if input is invalid?

Share your code in your next message, and let's walk through it together! 📝`,
    concepts: [
      'Code review techniques',
      'Logic verification',
      'Edge case testing',
      'Defensive programming'
    ],
    resources: [
      'Use check50 to verify correctness',
      'Run style50 for style feedback',
      'Test with various inputs',
      'Read through code line by line'
    ],
    next_steps: [
      'Share your code snippet',
      'Describe what you expect it to do',
      'Mention where you think the issue might be',
      'We\'ll work through it together'
    ],
    citations: []
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
  { label: '👀 Can you review my code?', type: 'code_review' },
]

export default function AssignmentHelpPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      content: `👋 **Welcome to the Assignment Helper!**

I'm here to guide you through your assignments using the Socratic method. I won't give you direct answers, but I'll help you:

• Break down problems into manageable steps
• Debug your code systematically  
• Understand key concepts
• Think through algorithms logically

**You can:**
- Ask questions about the assignment
- Share code snippets for review (click "Add code/context" button)
- Describe errors you're encountering
- Request help with algorithms or concepts

Let's work through this together! 🎓

**Quick tip:** Select your problem from the dropdown above, then start asking questions!`,
    }
  ])
  const [input, setInput] = useState('')
  const [contextInput, setContextInput] = useState('')
  const [selectedProblem, setSelectedProblem] = useState('')
  const [showContextBox, setShowContextBox] = useState(false)
  const [loading, setLoading] = useState(false)
  const [useMockData, setUseMockData] = useState(true)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = {
      role: 'user',
      content: input,
      userContext: contextInput || undefined,
      problemNumber: PROBLEMS.find(p => p.id === selectedProblem)?.name
    }

    setMessages(prev => [...prev, userMessage])
    setInput('')
    setContextInput('')
    setShowContextBox(false)
    setLoading(true)

    try {
      if (useMockData) {
        // Use mock data for demonstration
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        const questionLower = input.toLowerCase()
        let mockType = 'getting_started'
        
        if (questionLower.includes('error') || questionLower.includes('bug') || questionLower.includes('wrong') || questionLower.includes('doesn\'t work')) {
          mockType = 'debugging'
        } else if (questionLower.includes('algorithm') || questionLower.includes('approach') || questionLower.includes('solve')) {
          mockType = 'algorithm'
        } else if (questionLower.includes('code') || questionLower.includes('review') || questionLower.includes('look at') || contextInput.trim()) {
          mockType = 'code_review'
        }
        
        const assistantMessage: Message = {
          role: 'assistant',
          content: '',
          response: MOCK_RESPONSES[mockType]
        }
        
        setMessages(prev => [...prev, assistantMessage])
      } else {
        // Real API call
        const res = await fetch('http://localhost:8000/api/assignment-help', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            question: input,
            problem_number: PROBLEMS.find(p => p.id === selectedProblem)?.name,
            context: contextInput || undefined,
            course_id: 'cs50'
          }),
        })
        
        if (!res.ok) throw new Error('Failed to get help')
        const data = await res.json()
        
        const assistantMessage: Message = {
          role: 'assistant',
          content: '',
          response: data
        }
        
        setMessages(prev => [...prev, assistantMessage])
      }
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend is running and try again.',
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const handleHintClick = (type: string) => {
    const hintText = HINT_SUGGESTIONS.find(h => h.type === type)?.label || ''
    setInput(hintText)
  }

  return (
    <div className="flex h-screen bg-[#f7f7f5]">
      {/* Sidebar - Consistent with Student Chat */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-gray-200">
          <Logo size="sm" showText={true} />
        </div>

        {/* Primary Action - Subtle Outlined Button */}
        <div className="px-4 py-4">
          <button
            onClick={() => router.push('/student')}
            className="w-full px-4 py-2.5 bg-white border border-gray-300 hover:border-gray-400 text-gray-900 font-medium text-sm rounded-lg shadow-sm hover:shadow-md transition-all duration-200 flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <MessageCircle size={16} className="text-gray-600" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Navigation - Increased Spacing */}
        <nav className="px-4 py-2 space-y-1">
          <button
            onClick={() => router.push('/faq')}
            className="w-full px-4 py-3 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <HelpCircle size={18} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>FAQ</span>
          </button>
          <button
            onClick={() => router.push('/study-plan')}
            className="w-full px-4 py-3 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <BookOpen size={18} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Study Plan</span>
          </button>
          <button
            onClick={() => router.push('/assignment-help')}
            className="w-full px-4 py-3 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <FileText size={18} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Assignment Help</span>
          </button>
        </nav>
        
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto px-4 mt-6">
          <div className="px-4 mb-3">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recent Chats</div>
          </div>
          <div className="px-4 py-8 text-center">
            <div className="text-xs text-gray-400">No chat history yet</div>
          </div>
        </div>

        {/* Bottom */}
        <div className="px-4 py-4 border-t border-gray-200">
          <button
            onClick={() => router.push('/login')}
            className="w-full px-4 py-2.5 text-left text-sm text-gray-600 hover:text-gray-900 hover:bg-white rounded-lg transition-all duration-200 flex items-center gap-3 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <User size={18} className="text-gray-500" />
            <span>Switch Role</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="px-4 py-3 border-b border-gray-200 bg-white">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h1 className="text-2xl font-normal text-gray-900">Assignment Helper</h1>
                <p className="text-gray-600 text-sm">Get Socratic guidance on your assignments</p>
              </div>
              <label className="flex items-center gap-2 cursor-pointer text-sm">
                <input
                  type="checkbox"
                  checked={useMockData}
                  onChange={(e) => setUseMockData(e.target.checked)}
                  className="rounded"
                />
                <span className="text-gray-700">Demo mode</span>
              </label>
            </div>
            
            <div className="flex items-center gap-2">
              <label className="text-xs text-gray-600 whitespace-nowrap">Problem:</label>
              <select
                value={selectedProblem}
                onChange={(e) => setSelectedProblem(e.target.value)}
                className="flex-1 border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
              >
                <option value="">Select problem...</option>
                {PROBLEMS.map(problem => (
                  <option key={problem.id} value={problem.id}>
                    {problem.name}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.map((message, index) => (
              <div key={index}>
                {/* User Message */}
                {message.role === 'user' && (
                  <div className="ml-12">
                    <div className="bg-green-100 p-4 rounded-lg">
                      <div className="font-semibold mb-1 text-sm text-gray-600">
                        👤 You {message.problemNumber && `• ${message.problemNumber}`}
                      </div>
                      <div className="text-gray-800 whitespace-pre-wrap">
                        {message.content}
                      </div>
                      {message.userContext && (
                        <div className="mt-3 pt-3 border-t border-green-200">
                          <div className="text-xs font-semibold text-gray-600 mb-1">Code/Context:</div>
                          <pre className="bg-gray-900 text-gray-100 p-3 rounded text-xs overflow-x-auto">
                            {message.userContext}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* System Message */}
                {message.role === 'system' && (
                  <div className="bg-teal-50 border-2 border-teal-200 p-4 rounded-lg">
                    <div className="font-semibold mb-2 text-sm text-teal-800">
                      🎓 Assignment Helper
                    </div>
                    <div className="text-gray-800 whitespace-pre-wrap">
                      {message.content}
                    </div>
                  </div>
                )}

                {/* Assistant Message with Response */}
                {message.role === 'assistant' && message.response && (
                  <div className="mr-12">
                    <div className="bg-gray-50 p-4 rounded-lg border-l-4 border-green-500">
                      <div className="font-semibold mb-3 text-sm text-gray-600">
                        🤖 OpenTA Helper
                      </div>

                      {/* Guidance */}
                      <div className="mb-4">
                        <div className="text-sm font-bold text-green-800 mb-2">💡 Guidance:</div>
                        <div className="text-gray-800 whitespace-pre-wrap text-sm">
                          {message.response.guidance}
                        </div>
                      </div>

                      {/* Collapsible Details */}
                      <details className="mb-3">
                        <summary className="text-sm font-bold text-blue-800 cursor-pointer hover:text-blue-600">
                          📚 Key Concepts ({message.response.concepts.length})
                        </summary>
                        <div className="mt-2 ml-4 space-y-1">
                          {message.response.concepts.map((concept, idx) => (
                            <div key={idx} className="text-sm text-gray-700">• {concept}</div>
                          ))}
                        </div>
                      </details>

                      <details className="mb-3">
                        <summary className="text-sm font-bold text-purple-800 cursor-pointer hover:text-purple-600">
                          📖 Resources ({message.response.resources.length})
                        </summary>
                        <div className="mt-2 ml-4 space-y-1">
                          {message.response.resources.map((resource, idx) => (
                            <div key={idx} className="text-sm text-gray-700">• {resource}</div>
                          ))}
                        </div>
                      </details>

                      <details className="mb-3">
                        <summary className="text-sm font-bold text-orange-800 cursor-pointer hover:text-orange-600">
                          ➡️ Next Steps ({message.response.next_steps.length})
                        </summary>
                        <div className="mt-2 ml-4 space-y-1">
                          {message.response.next_steps.map((step, idx) => (
                            <div key={idx} className="text-sm text-gray-700">{idx + 1}. {step}</div>
                          ))}
                        </div>
                      </details>

                      {/* Citations */}
                      {message.response.citations && message.response.citations.length > 0 && (
                        <details>
                          <summary className="text-sm font-bold text-gray-800 cursor-pointer hover:text-gray-600">
                            📎 Citations ({message.response.citations.length})
                          </summary>
                          <div className="mt-2 space-y-2">
                            {message.response.citations.map((citation, idx) => (
                              <div key={idx} className="bg-white border border-gray-200 rounded p-3 text-xs">
                                <div className="font-semibold text-gray-800 mb-1">
                                  {citation.source} - {citation.section}
                                </div>
                                <div className="text-gray-600">{citation.text}</div>
                              </div>
                            ))}
                          </div>
                        </details>
                      )}
                    </div>
                  </div>
                )}

                {/* Simple Assistant Message (errors, etc) */}
                {message.role === 'assistant' && !message.response && (
                  <div className="mr-12">
                    <div className="bg-red-50 border-l-4 border-red-400 p-4 rounded-lg">
                      <div className="font-semibold mb-1 text-sm text-gray-600">
                        🤖 OpenTA Helper
                      </div>
                      <div className="text-gray-800">
                        {message.content}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {loading && (
              <div className="mr-12">
                <div className="bg-gray-100 p-4 rounded-lg animate-pulse">
                  <div className="font-semibold mb-1 text-sm text-gray-600">
                    🤖 OpenTA Helper
                  </div>
                  <div className="text-gray-600 flex items-center gap-2">
                    <span>Analyzing your question</span>
                    <span className="flex gap-1">
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></span>
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></span>
                      <span className="w-2 h-2 bg-green-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></span>
                    </span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="border-t border-gray-200 bg-white p-3">
          <div className="max-w-4xl mx-auto space-y-2">
            {/* Quick Hints */}
            <div>
              <div className="text-xs font-semibold text-gray-500 mb-1.5">💡 Quick Hints:</div>
            <div className="flex flex-wrap gap-1.5">
              {HINT_SUGGESTIONS.map((hint) => (
                <button
                  key={hint.type}
                  onClick={() => handleHintClick(hint.type)}
                  className="px-2.5 py-1 bg-green-50 hover:bg-green-100 text-green-800 rounded-full text-xs transition"
                >
                  {hint.label}
                </button>
              ))}
              </div>
            </div>

            <div className="space-y-2">
          {/* Context/Code Input (Collapsible) */}
          {showContextBox && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700">
                📋 Code snippet or additional context (optional):
              </label>
              <textarea
                value={contextInput}
                onChange={(e) => setContextInput(e.target.value)}
                placeholder="Paste your code here or describe what you've tried..."
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 font-mono text-sm"
              />
            </div>
          )}

          {/* Main Input */}
          <div className="flex gap-2">
            <button
              onClick={() => setShowContextBox(!showContextBox)}
              className={`px-3 py-2 rounded-lg transition text-sm ${
                showContextBox 
                  ? 'bg-green-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              ➕ Code
            </button>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question or describe your problem..."
              rows={2}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500 resize-none text-sm"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-medium text-sm"
            >
              Send
            </button>
          </div>
          
            <div className="text-xs text-gray-500">
              💡 Tip: Press Enter to send, Shift+Enter for new line. Click "➕ Code" to share code snippets.
            </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
