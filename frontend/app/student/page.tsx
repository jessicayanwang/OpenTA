'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle, HelpCircle, BookOpen, FileText, User, Send, Sparkles, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import Logo from '@/components/Logo'

interface Citation {
  source: string
  section: string
  text: string
  relevance_score: number
}

interface Message {
  role: 'user' | 'assistant' | 'system'
  content: string
  citations?: Citation[]
  confidence?: number
  suggestedQuestions?: string[]
}

export default function Home() {
  const router = useRouter()
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const [showWelcome, setShowWelcome] = useState(true)
  const [showTour, setShowTour] = useState(false)

  // Check if this is the user's first visit
  useEffect(() => {
    const hasVisited = localStorage.getItem('hasVisitedStudent')
    if (!hasVisited) {
      setShowTour(true)
      localStorage.setItem('hasVisitedStudent', 'true')
    }
  }, [])

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return
    
    setShowWelcome(false)
    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev: Message[]) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question: input,
          course_id: 'cs50'
        }),
      })

      if (!response.ok) {
        throw new Error('Failed to get response')
      }

      const data = await response.json()
      
      // Generate suggested follow-up questions based on the topic
      const suggestedQuestions = generateFollowUps(input, data.citations)
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: data.answer,
        citations: data.citations,
        confidence: data.confidence,
        suggestedQuestions
      }

      setMessages((prev: Message[]) => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend is running.',
      }
      setMessages((prev: Message[]) => [...prev, errorMessage])
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

  const generateFollowUps = (question: string, citations: Citation[]) => {
    const q = question.toLowerCase()
    
    if (q.includes('due') || q.includes('deadline')) {
      return [
        'What is the late policy?',
        'How do late days work?',
        'When is the final project due?'
      ]
    } else if (q.includes('late') || q.includes('policy')) {
      return [
        'What is the grading breakdown?',
        'What is the collaboration policy?',
        'When are office hours?'
      ]
    } else if (q.includes('office') || q.includes('help')) {
      return [
        'What is the collaboration policy?',
        'How do I submit assignments?',
        'When is the midterm?'
      ]
    } else if (q.includes('mario') || q.includes('problem') || q.includes('assignment')) {
      return [
        'What other problems are in Problem Set 1?',
        'What is the grading rubric?',
        'How do I get help with assignments?'
      ]
    }
    
    return [
      'Tell me about the grading policy',
      'What are the office hours?',
      'When is Problem Set 2 due?'
    ]
  }

  const suggestedStarters = [
    'When is Problem Set 1 due?',
    'What is the late policy?',
    'What are the office hours?',
    'Help me understand the Mario problem'
  ]

  const handleNewChat = () => {
    setMessages([])
    setShowWelcome(true)
  }

  return (
    <div className="flex h-screen bg-[#f7f7f5]">
      {/* Sidebar - Refined Academic Minimalist */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo - Editorial Typography */}
        <div className="p-4 border-b border-gray-200">
          <Logo size="sm" showText={true} />
        </div>

        {/* Primary Action - Subtle Outlined Button */}
        <div className="px-4 py-4">
          <button
            onClick={handleNewChat}
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

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto bg-[#f7f7f5]">
          {showWelcome && messages.length === 0 ? (
            <div className="max-w-4xl mx-auto px-8 py-12">
              <div className="text-center mb-12">
                <h1 className="font-normal text-6xl tracking-tight text-gray-900 mb-5">
                  Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}
                </h1>
                <p className="text-gray-600 text-xl">How can I help you learn today?</p>
              </div>

              <div className="grid grid-cols-2 gap-4 mb-8">
                {suggestedStarters.map((starter, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(starter)}
                    className="p-5 text-left bg-white rounded-2xl shadow-sm hover:shadow-lg hover:-translate-y-1 transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30 border border-gray-100"
                  >
                    <div className="text-sm text-gray-700 leading-relaxed">{starter}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto px-8 py-6 space-y-4 bg-[#f7f7f5]">
              {messages.map((message, index) => (
                <div key={index}>
                  {message.role === 'user' ? (
                    /* User Message - Brand Orange */
                    <div className="flex justify-end mb-4">
                      <div className="bg-gradient-to-br from-orange-500 to-orange-600 px-4 py-2.5 rounded-2xl max-w-lg shadow-sm">
                        <div className="text-white text-sm leading-relaxed">
                          {message.content}
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Assistant Message - Light Gray */
                    <div className="flex gap-3 mb-4">
                      <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                        <Sparkles size={16} className="text-white" />
                      </div>
                      <div className="flex-1 max-w-lg">
                        <div className="bg-white border border-gray-200 rounded-xl px-4 py-3 shadow-sm">
                          <div className="text-gray-800 text-sm leading-relaxed prose prose-sm max-w-none">
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                          </div>
                          
                          {message.confidence !== undefined && (
                            <div className="mt-3 text-xs text-gray-500 font-medium">
                              Confidence: {(message.confidence * 100).toFixed(0)}%
                            </div>
                          )}

                          {/* Citations - Academic Pill Style */}
                          {message.citations && message.citations.length > 0 && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <div className="flex flex-wrap gap-1.5">
                                {message.citations.map((citation, idx) => (
                                  <span key={idx} className="inline-flex items-center gap-1 px-2 py-1 bg-orange-50 text-orange-700 text-xs font-medium rounded-full border border-orange-200">
                                    <FileText size={12} />
                                    {citation.source} • {citation.section}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Suggested Follow-up Questions */}
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
                </div>
              ))}
              
              {loading && (
                <div className="flex gap-3 mb-4">
                  <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center flex-shrink-0 shadow-sm">
                    <Sparkles size={16} className="text-white" />
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
          )}
        </div>

        {/* Input Area - Compact */}
        <div className="border-t border-gray-200 bg-white px-4 py-3">
          <div className="max-w-4xl mx-auto">
            <div className="relative flex items-center gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question..."
                className="flex-1 px-4 py-2.5 bg-white border border-gray-300 hover:border-gray-400 focus:border-orange-500 rounded-lg text-gray-900 text-sm placeholder:text-gray-500 resize-none shadow-sm hover:shadow focus:shadow transition-all duration-200 focus:outline-none focus:ring-1 focus:ring-orange-500"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="p-2.5 bg-gradient-to-br from-orange-500 to-orange-600 hover:from-orange-600 hover:to-orange-700 text-white rounded-lg shadow-sm hover:shadow-md transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
              >
                <Send size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Welcome Tour Modal */}
      {showTour && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-6">
          <div className="bg-white rounded-2xl max-w-2xl w-full p-8 shadow-2xl">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-12 h-12 bg-gradient-to-br from-accent-500 to-accent-700 rounded-xl flex items-center justify-center">
                <Sparkles size={24} className="text-white" />
              </div>
              <h2 className="text-3xl font-serif font-semibold text-[#1F1D20]">Welcome to OpenTA!</h2>
            </div>
            
            <p className="text-[#6F6B65] text-lg mb-8 leading-relaxed">
              Your AI teaching assistant is ready to help you succeed. Here's what you can do:
            </p>

            <div className="space-y-6 mb-8">
              <div className="flex gap-4">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <MessageCircle size={20} className="text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#1F1D20] mb-1">Ask Questions</h3>
                  <p className="text-sm text-[#6F6B65]">
                    Get instant answers about course logistics, deadlines, policies, and content — all backed by citations from your course materials.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BookOpen size={20} className="text-green-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#1F1D20] mb-1">Create Study Plans</h3>
                  <p className="text-sm text-[#6F6B65]">
                    Navigate to Study Plan in the sidebar to generate personalized schedules based on your goals and availability.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <FileText size={20} className="text-purple-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#1F1D20] mb-1">Get Assignment Help</h3>
                  <p className="text-sm text-[#6F6B65]">
                    Stuck on a problem? Visit Assignment Help for Socratic guidance that helps you learn without giving away answers.
                  </p>
                </div>
              </div>

              <div className="flex gap-4">
                <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <HelpCircle size={20} className="text-orange-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-[#1F1D20] mb-1">Check the FAQ</h3>
                  <p className="text-sm text-[#6F6B65]">
                    Browse professor-verified answers to common questions for quick reference.
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-accent-50 border border-accent-200 rounded-xl p-4 mb-6">
              <p className="text-sm text-accent-800">
                <strong>💡 Pro Tip:</strong> All answers include citations showing exactly where the information comes from. Click on citation badges to see sources!
              </p>
            </div>

            <button
              onClick={() => setShowTour(false)}
              className="w-full px-6 py-3 bg-accent-600 hover:bg-accent-700 text-white font-semibold rounded-xl shadow-sm transition-all duration-150"
            >
              Got it, let's start!
            </button>
          </div>
        </div>
      )}
    </div>
  )
}
