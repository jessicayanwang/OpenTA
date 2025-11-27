'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle, HelpCircle, BookOpen, FileText, User, GraduationCap, Bot, Lightbulb, Library, ArrowRight, Paperclip, Rocket, Wrench, Bug, Code2, Eye } from 'lucide-react'
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
  suggestedQuestions?: string[]
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
  { label: 'How do I start?', type: 'getting_started', icon: 'rocket' },
  { label: 'My code has an error', type: 'debugging', icon: 'bug' },
  { label: 'What algorithm should I use?', type: 'algorithm', icon: 'code' },
  { label: 'Can you review my code?', type: 'code_review', icon: 'eye' },
]

export default function AssignmentHelpPage() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      content: `Welcome to the Assignment Helper!

I'm here to guide you through your assignments using the Socratic method. I won't give you direct answers, but I'll help you:

• Break down problems into manageable steps
• Debug your code systematically  
• Understand key concepts
• Think through algorithms logically

You can:
- Ask questions about the assignment
- Share code snippets for review (click "Add code/context" button)
- Describe errors you're encountering
- Request help with algorithms or concepts

Let's work through this together!

Quick tip: Select your problem from the dropdown above, then start asking questions!`,
      suggestedQuestions: ['How do I start?', 'My code has an error', 'What algorithm should I use?', 'Can you review my code?']
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
      <aside className="w-56 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="px-3 py-2 border-b border-gray-200">
          <Logo size="sm" showText={true} />
        </div>

        {/* Primary Action - Subtle Outlined Button */}
        <div className="px-3 py-3">
          <button
            onClick={() => router.push('/student')}
            className="w-full px-3 py-2 text-sm text-gray-700 bg-white border border-gray-300 hover:border-gray-400 rounded-lg transition-all duration-200 flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <MessageCircle size={16} className="text-gray-600" />
            <span>New Chat</span>
          </button>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-2 space-y-0.5">
          <button
            onClick={() => router.push('/faq')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <HelpCircle size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>FAQ</span>
          </button>
          <button
            onClick={() => router.push('/study-plan')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <BookOpen size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Self-study Room</span>
          </button>
          <button
            onClick={() => router.push('/assignment-help')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <FileText size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Assignment Help</span>
          </button>
        </nav>
        
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto px-3 mt-4">
          <div className="mb-2">
            <div className="text-xs font-semibold text-gray-500 uppercase tracking-wider">Recent Chats</div>
          </div>
          <div className="py-6 text-center">
            <div className="text-xs text-gray-400">No chat history yet</div>
          </div>
        </div>

        {/* Bottom */}
        <div className="px-4 py-3 border-t border-gray-200">
          <button
            onClick={() => router.push('/login')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-all duration-200 flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <User size={16} className="text-gray-500" />
            <span>Switch Role</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        <div className="px-8 py-2 bg-[#f7f7f5]">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4 flex-1">
              <h1 className="text-xl font-normal text-gray-900 whitespace-nowrap">Assignment Helper</h1>
              <div className="flex items-center gap-2 flex-1">
                <label className="text-xs text-gray-600 whitespace-nowrap">Problem:</label>
                <select
                  value={selectedProblem}
                  onChange={(e) => setSelectedProblem(e.target.value)}
                  className="flex-1 max-w-xs border border-gray-300 rounded-lg px-3 py-1.5 text-sm"
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
            <label className="flex items-center gap-2 cursor-pointer text-xs">
              <input
                type="checkbox"
                checked={useMockData}
                onChange={(e) => setUseMockData(e.target.checked)}
                className="rounded"
              />
              <span className="text-gray-700 whitespace-nowrap">Demo mode</span>
            </label>
          </div>
        </div>

        {/* Chat Container */}
        <div className="flex-1 overflow-y-auto bg-[#f7f7f5] py-4">
          <div className="max-w-4xl mx-auto px-8 space-y-3">
            {messages.map((message, index) => (
              <div key={index}>
                {/* User Message */}
                {message.role === 'user' && (
                  <div className="flex justify-end mb-4">
                    <div className="bg-gradient-to-br from-orange-500 to-orange-600 px-4 py-2.5 rounded-2xl max-w-lg shadow-sm">
                      <div className="text-white text-sm leading-relaxed whitespace-pre-wrap">
                        {message.content}
                      </div>
                      {message.userContext && (
                        <div className="mt-2 pt-2 border-t border-orange-400">
                          <div className="text-xs font-medium text-orange-100 mb-1">Code:</div>
                          <pre className="bg-black/20 text-white p-2 rounded text-xs overflow-x-auto">
                            {message.userContext}
                          </pre>
                        </div>
                      )}
                    </div>
                  </div>
                )}

                {/* System Message */}
                {message.role === 'system' && (
                  <div className="flex gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                      <GraduationCap size={16} className="text-white" />
                    </div>
                    <div className="flex-1 max-w-lg">
                      <div className="bg-gray-50 border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
                        <div className="text-gray-800 text-sm leading-relaxed whitespace-pre-wrap">
                          {message.content}
                        </div>
                        
                        {/* Suggested Questions */}
                        {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
                          <div className="mt-3 pt-3 border-t border-gray-200">
                            <div className="text-xs text-gray-500 mb-2">Suggested:</div>
                            <div className="flex flex-wrap gap-2">
                              {message.suggestedQuestions.map((question, idx) => (
                                <button
                                  key={idx}
                                  onClick={() => setInput(question)}
                                  className="text-xs text-gray-700 hover:text-orange-600 bg-gray-50 hover:bg-orange-50 px-3 py-1.5 rounded-full transition-all duration-200 border border-gray-200 hover:border-orange-300 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
                                >
                                  {question}
                                </button>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Assistant Message with Response */}
                {message.role === 'assistant' && message.response && (
                  <div className="flex gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                      <Bot size={16} className="text-white" />
                    </div>
                    <div className="flex-1 max-w-lg">
                      <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-sm">

                      {/* Guidance */}
                      <div className="mb-3">
                        <div className="text-xs font-semibold text-orange-600 mb-1.5 flex items-center gap-1"><Lightbulb size={12} /> Guidance:</div>
                        <div className="text-gray-800 whitespace-pre-wrap text-sm leading-relaxed">
                          {message.response.guidance}
                        </div>
                      </div>

                      {/* Collapsible Details */}
                      <details className="mb-2">
                        <summary className="text-xs font-semibold text-gray-600 cursor-pointer hover:text-orange-600 flex items-center gap-1">
                          <Library size={12} /> Key Concepts ({message.response.concepts.length})
                        </summary>
                        <div className="mt-1.5 ml-3 space-y-0.5">
                          {message.response.concepts.map((concept, idx) => (
                            <div key={idx} className="text-xs text-gray-700">• {concept}</div>
                          ))}
                        </div>
                      </details>

                      <details className="mb-2">
                        <summary className="text-xs font-semibold text-gray-600 cursor-pointer hover:text-orange-600 flex items-center gap-1">
                          <BookOpen size={12} /> Resources ({message.response.resources.length})
                        </summary>
                        <div className="mt-1.5 ml-3 space-y-0.5">
                          {message.response.resources.map((resource, idx) => (
                            <div key={idx} className="text-xs text-gray-700">• {resource}</div>
                          ))}
                        </div>
                      </details>

                      <details className="mb-2">
                        <summary className="text-xs font-semibold text-gray-600 cursor-pointer hover:text-orange-600 flex items-center gap-1">
                          <ArrowRight size={12} /> Next Steps ({message.response.next_steps.length})
                        </summary>
                        <div className="mt-1.5 ml-3 space-y-0.5">
                          {message.response.next_steps.map((step, idx) => (
                            <div key={idx} className="text-xs text-gray-700">{idx + 1}. {step}</div>
                          ))}
                        </div>
                      </details>

                      {/* Citations */}
                      {message.response.citations && message.response.citations.length > 0 && (
                        <details>
                          <summary className="text-xs font-semibold text-gray-600 cursor-pointer hover:text-orange-600 flex items-center gap-1">
                            <Paperclip size={12} /> Citations ({message.response.citations.length})
                          </summary>
                          <div className="mt-1.5 flex flex-wrap gap-1.5">
                            {message.response.citations.map((citation, idx) => (
                              <span key={idx} className="inline-flex items-center gap-1 px-2 py-1 bg-orange-50 text-orange-700 text-xs font-medium rounded-full border border-orange-200">
                                {citation.source} • {citation.section}
                              </span>
                            ))}
                          </div>
                        </details>
                      )}
                      </div>
                    </div>
                  </div>
                )}

                {/* Simple Assistant Message (errors, etc) */}
                {message.role === 'assistant' && !message.response && (
                  <div className="flex gap-3 mb-4">
                    <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                      <Bot size={16} className="text-white" />
                    </div>
                    <div className="flex-1 max-w-lg">
                      <div className="bg-red-50 border border-red-200 rounded-xl px-4 py-3 shadow-sm">
                        <div className="text-gray-800 text-sm">
                        {message.content}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
            
            {loading && (
              <div className="flex gap-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                  <span className="text-white text-sm">🤖</span>
                </div>
                <div className="flex-1 max-w-lg">
                  <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
                    <div className="flex items-center gap-3 text-gray-600">
                      <div className="flex gap-1.5">
                        <span className="w-2 h-2 bg-orange-500 rounded-full animate-bounce"></span>
                        <span className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></span>
                        <span className="w-2 h-2 bg-orange-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></span>
                      </div>
                      <span className="text-sm">Thinking...</span>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area - Fixed at bottom */}
        <div className="bg-[#f7f7f5] px-4 py-3">
          <div className="max-w-4xl mx-auto">
            <div className="space-y-2">
          {/* Context/Code Input (Collapsible) */}
          {showContextBox && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-700 flex items-center gap-1.5">
                <FileText size={14} /> Code snippet or additional context (optional):
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
          <div className="flex items-center gap-2">
            <button
              onClick={() => setShowContextBox(!showContextBox)}
              className={`p-2.5 rounded-lg transition text-sm ${
                showContextBox 
                  ? 'bg-orange-600 text-white' 
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
              title="Add code snippet"
            >
              ➕
            </button>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question or describe your problem..."
              className="flex-1 px-4 py-2.5 bg-white border border-gray-300 hover:border-gray-400 focus:border-orange-500 rounded-lg text-gray-900 text-sm placeholder:text-gray-500 shadow-sm hover:shadow focus:shadow transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-orange-500"
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="p-2.5 bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
            </button>
          </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
