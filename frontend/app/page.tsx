'use client'

import { useState, useEffect, useRef } from 'react'

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
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'system',
      content: '👋 Welcome to OpenTA! I\'m your AI teaching assistant for CS50. I can help you with course logistics, policies, and assignment details. All my answers are grounded in official course materials with citations.\n\nTry asking me about deadlines, policies, or assignment requirements!',
      suggestedQuestions: [
        'When is Problem Set 1 due?',
        'What is the late policy?',
        'What are the office hours?'
      ]
    }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async () => {
    if (!input.trim()) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages(prev => [...prev, userMessage])
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

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please make sure the backend is running.',
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

  return (
    <main className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-5xl mx-auto p-6">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            🎓 OpenTA
          </h1>
          <p className="text-gray-600">
            Your AI Teaching Assistant - Ask questions about CS50 and get answers with citations
          </p>
        </div>

        {/* Chat Container */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6 min-h-[500px] max-h-[600px] overflow-y-auto">
          <div className="space-y-4">
            {messages.map((message, index) => (
              <div key={index}>
                <div
                  className={`p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-indigo-100 ml-12'
                      : message.role === 'system'
                      ? 'bg-green-50 border-2 border-green-200'
                      : 'bg-gray-100 mr-12'
                  }`}
                >
                  <div className="font-semibold mb-1 text-sm text-gray-600">
                    {message.role === 'user' ? '👤 You' : message.role === 'system' ? '🎓 OpenTA System' : '🤖 OpenTA'}
                  </div>
                  <div className="text-gray-800 whitespace-pre-wrap">
                    {message.content}
                  </div>
                  
                  {message.confidence !== undefined && (
                    <div className="mt-2 text-xs text-gray-500">
                      Confidence: {(message.confidence * 100).toFixed(0)}%
                    </div>
                  )}
                </div>

                  {/* Citations */}
                  {message.citations && message.citations.length > 0 && (
                    <div className="mt-2 mr-12 space-y-2">
                      <div className="text-sm font-semibold text-gray-600">
                        📚 Sources:
                      </div>
                      {message.citations.map((citation, citIndex) => (
                        <div
                          key={citIndex}
                          className="bg-blue-50 border-l-4 border-blue-400 p-3 rounded text-sm"
                        >
                          <div className="font-semibold text-blue-900 mb-1">
                            {citation.source} - {citation.section}
                          </div>
                          <div className="text-gray-700 text-xs">
                            {citation.text}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            Relevance: {(citation.relevance_score * 100).toFixed(0)}%
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Suggested Follow-up Questions */}
                  {message.suggestedQuestions && message.suggestedQuestions.length > 0 && (
                    <div className="mt-3 mr-12">
                      <div className="text-xs font-semibold text-gray-500 mb-2">
                        💡 You might also want to ask:
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {message.suggestedQuestions.map((question, qIndex) => (
                          <button
                            key={qIndex}
                            onClick={() => setInput(question)}
                            className="px-3 py-1 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 rounded-full text-xs transition"
                          >
                            {question}
                          </button>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ))}
              
              {loading && (
                <div className="bg-gray-100 p-4 rounded-lg mr-12 animate-pulse">
                  <div className="font-semibold mb-1 text-sm text-gray-600">
                    🤖 OpenTA
                  </div>
                  <div className="text-gray-600 flex items-center gap-2">
                    <span>Searching course materials</span>
                    <span className="flex gap-1">
                      <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{animationDelay: '0ms'}}></span>
                      <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{animationDelay: '150ms'}}></span>
                      <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce" style={{animationDelay: '300ms'}}></span>
                    </span>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>
        </div>

        {/* Input Area */}
        <div className="bg-white rounded-lg shadow-lg p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask a question about the course..."
              className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition font-semibold"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </main>
  )
}
