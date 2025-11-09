'use client'

import { useState, useEffect, useRef } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle, HelpCircle, BookOpen, FileText, User, Send, Sparkles, ChevronRight } from 'lucide-react'
import ReactMarkdown from 'react-markdown'

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
    <div className="flex h-screen bg-bg">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-[#E9E4DE] flex flex-col">
        {/* Logo */}
        <div className="px-4 py-5 border-b border-[#E9E4DE]">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 bg-gradient-to-br from-accent-500 to-accent-700 rounded-lg flex items-center justify-center text-white font-semibold text-base">
              O
            </div>
            <span className="font-serif font-semibold text-lg text-[#1F1D20]">OpenTA</span>
          </div>
        </div>

        {/* Primary Action */}
        <div className="p-3">
          <button
            onClick={handleNewChat}
            className="w-full px-4 py-2 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 text-white font-medium text-sm rounded-pill shadow-sm hover:shadow-md transition-all duration-150 flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
          >
            <MessageCircle size={16} />
            <span>New Chat</span>
          </button>
        </div>

        {/* Navigation */}
        <nav className="px-3 py-2 space-y-0.5">
          <button
            onClick={() => router.push('/faq')}
            className="w-full px-3 py-2 text-left text-sm text-[#6F6B65] hover:text-[#1F1D20] hover:bg-[#F9F6F1] rounded-lg transition-all duration-120 flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
          >
            <HelpCircle size={18} />
            <span className="font-medium">FAQ</span>
          </button>
          <button
            onClick={() => router.push('/study-plan')}
            className="w-full px-3 py-2 text-left text-sm text-[#6F6B65] hover:text-[#1F1D20] hover:bg-[#F9F6F1] rounded-lg transition-all duration-120 flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
          >
            <BookOpen size={18} />
            <span className="font-medium">Study Plan</span>
          </button>
          <button
            onClick={() => router.push('/assignment-help')}
            className="w-full px-3 py-2 text-left text-sm text-[#6F6B65] hover:text-[#1F1D20] hover:bg-[#F9F6F1] rounded-lg transition-all duration-120 flex items-center gap-2.5 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
          >
            <FileText size={18} />
            <span className="font-medium">Assignment Help</span>
          </button>
        </nav>
        
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto px-3 mt-4">
          <div className="px-3 mb-2">
            <div className="text-xs font-semibold text-[#8F8780] uppercase tracking-wider">Recent Chats</div>
          </div>
          <div className="px-3 py-6 text-center">
            <div className="text-xs text-[#B8B1A8]">No chat history yet</div>
          </div>
        </div>

        {/* Bottom */}
        <div className="p-3 border-t border-[#E9E4DE]">
          <button
            onClick={() => router.push('/login')}
            className="w-full px-3 py-2 text-left text-sm text-[#6F6B65] hover:text-[#1F1D20] hover:bg-[#F9F6F1] rounded-lg transition-all duration-120 flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
          >
            <User size={18} />
            <span>Switch Role</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {showWelcome && messages.length === 0 ? (
            <div className="max-w-3xl mx-auto px-6 py-20">
              <div className="text-center mb-16">
                <h1 className="font-serif font-semibold text-5xl tracking-tight text-[#1F1D20] mb-4">
                  Good {new Date().getHours() < 12 ? 'morning' : new Date().getHours() < 18 ? 'afternoon' : 'evening'}
                </h1>
                <p className="text-[#6F6B65] text-lg">How can I help you learn today?</p>
              </div>

              <div className="grid grid-cols-2 gap-3 mb-8">
                {suggestedStarters.map((starter, i) => (
                  <button
                    key={i}
                    onClick={() => setInput(starter)}
                    className="p-4 text-left bg-white border border-[#E9E4DE] hover:border-[#D9D3CC] hover:bg-[#F9F6F1] rounded-xl shadow-xs hover:shadow-sm transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
                  >
                    <div className="text-sm text-[#4A4745] leading-relaxed">{starter}</div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="max-w-3xl mx-auto px-6 py-8 space-y-6">
              {messages.map((message, index) => (
                <div key={index}>
                  {message.role === 'user' ? (
                    /* User Message */
                    <div className="flex justify-end mb-8">
                      <div className="bg-accent-100 border border-accent-200 px-5 py-4 rounded-2xl max-w-2xl">
                        <div className="text-[#1F1D20] text-sm leading-relaxed">
                          {message.content}
                        </div>
                      </div>
                    </div>
                  ) : (
                    /* Assistant Message */
                    <div className="flex gap-4 mb-8">
                      <div className="w-9 h-9 bg-gradient-to-br from-accent-500 to-accent-700 rounded-full flex items-center justify-center flex-shrink-0">
                        <Sparkles size={18} className="text-white" />
                      </div>
                      <div className="flex-1 max-w-2xl">
                        <div className="bg-white border border-[#E9E4DE] rounded-2xl px-5 py-4 shadow-sm">
                          <div className="text-[#1F1D20] text-sm leading-relaxed prose prose-sm max-w-none">
                            <ReactMarkdown>{message.content}</ReactMarkdown>
                          </div>
                          
                          {message.confidence !== undefined && (
                            <div className="mt-2 text-xs text-gray-500">
                              Confidence: {(message.confidence * 100).toFixed(0)}%
                            </div>
                          )}

                          {/* Citations - Compact Collapsible Format */}
                          {message.citations && message.citations.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-[#E9E4DE]">
                              <div className="flex flex-wrap gap-2">
                                {message.citations.map((citation, idx) => (
                                  <span key={idx} className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-accent-100 text-accent-700 text-xs font-medium rounded-pill border border-accent-200">
                                    <FileText size={12} />
                                    {citation.source} • {citation.section}
                                  </span>
                                ))}
                              </div>
                            </div>
                          )}

                          {/* Suggested Follow-up Questions */}
                          {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
                            <div className="mt-4 pt-4 border-t border-[#E9E4DE]">
                              <div className="text-xs font-medium text-[#6F6B65] mb-3">Suggested follow-ups</div>
                              <div className="space-y-2">
                                {message.suggestedQuestions.map((question, idx) => (
                                  <button
                                    key={idx}
                                    onClick={() => setInput(question)}
                                    className="w-full text-left text-xs text-[#4A4745] hover:text-[#1F1D20] bg-[#F9F6F1] hover:bg-neutral-100 px-4 py-2.5 rounded-xl transition-all duration-120 flex items-center justify-between group focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
                                  >
                                    <span>{question}</span>
                                    <ChevronRight size={14} className="text-[#6F6B65] group-hover:text-accent-600 transition-colors" />
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
                <div className="flex gap-4 mb-8">
                  <div className="w-9 h-9 bg-gradient-to-br from-accent-500 to-accent-700 rounded-full flex items-center justify-center flex-shrink-0">
                    <Sparkles size={18} className="text-white" />
                  </div>
                  <div className="flex-1 max-w-2xl">
                    <div className="bg-white border border-[#E9E4DE] rounded-2xl px-5 py-4 shadow-sm">
                      <div className="flex items-center gap-3 text-[#6F6B65]">
                        <div className="flex gap-1.5">
                          <span className="w-2 h-2 bg-accent-500 rounded-full animate-bounce"></span>
                          <span className="w-2 h-2 bg-accent-500 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></span>
                          <span className="w-2 h-2 bg-accent-500 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></span>
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

        {/* Input Area */}
        <div className="border-t border-[#E9E4DE] bg-white p-4">
          <div className="max-w-3xl mx-auto px-6">
            <div className="relative">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Ask a question..."
                rows={2}
                className="w-full px-4 py-2.5 pr-12 bg-white border border-[#E9E4DE] hover:border-[#D9D3CC] focus:border-accent-500 rounded-xl text-[#1F1D20] text-sm placeholder:text-[#6F6B65] leading-relaxed resize-none shadow-xs transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
              />
              <button
                onClick={sendMessage}
                disabled={loading || !input.trim()}
                className="absolute bottom-2 right-2 p-2 bg-accent-600 hover:bg-accent-700 active:bg-accent-800 text-white rounded-full shadow-sm transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed focus:outline-none focus:ring-2 focus:ring-accent-500 focus:ring-opacity-40"
              >
                <Send size={14} />
              </button>
            </div>
            <div className="mt-2 text-xs text-[#6F6B65]">
              Press Enter to send, Shift+Enter for new line
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
