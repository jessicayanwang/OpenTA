'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'

interface FAQItem {
  question: string
  answer: string
  created_at: string
  created_by: string
}

export default function FAQPage() {
  const router = useRouter()
  const [faqItems, setFaqItems] = useState<FAQItem[]>([])
  const [loading, setLoading] = useState(true)
  const [expandedIndex, setExpandedIndex] = useState<number | null>(null)

  useEffect(() => {
    loadFAQ()
  }, [])

  const loadFAQ = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/faq?course_id=cs50')
      const data = await res.json()
      setFaqItems(data.faq)
    } catch (error) {
      console.error('Error loading FAQ:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex h-screen bg-[#f7f7f5]">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gradient-to-br from-orange-400 to-orange-600 rounded-lg flex items-center justify-center text-white font-bold">
              O
            </div>
            <span className="font-semibold text-gray-900">OpenTA</span>
          </div>
        </div>

        {/* Main Navigation */}
        <div className="p-3 border-b border-gray-200">
          <button
            onClick={() => router.push('/student')}
            className="w-full px-4 py-2.5 bg-gradient-to-br from-orange-400 to-orange-600 text-white rounded-lg hover:from-orange-500 hover:to-orange-700 transition text-sm font-medium flex items-center justify-center gap-2"
          >
            <span>💬</span>
            <span>New Chat</span>
          </button>
        </div>

        <div className="p-3 space-y-1">
          <button
            onClick={() => router.push('/faq')}
            className="w-full px-3 py-2.5 text-left text-sm bg-gray-100 text-gray-900 rounded-lg transition flex items-center gap-3"
          >
            <span className="text-lg">❓</span>
            <span className="font-medium">FAQ</span>
          </button>
          <button
            onClick={() => router.push('/study-plan')}
            className="w-full px-3 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition flex items-center gap-3"
          >
            <span className="text-lg">📚</span>
            <span className="font-medium">Study Plan</span>
          </button>
          <button
            onClick={() => router.push('/assignment-help')}
            className="w-full px-3 py-2.5 text-left text-sm text-gray-700 hover:bg-gray-100 rounded-lg transition flex items-center gap-3"
          >
            <span className="text-lg">📝</span>
            <span className="font-medium">Assignment Help</span>
          </button>
        </div>
        
        {/* Chat History */}
        <div className="flex-1 overflow-y-auto px-3">
          <div className="text-xs font-semibold text-gray-500 px-3 py-2 mt-2">RECENT CHATS</div>
          <div className="text-xs text-gray-400 px-3 py-2">No chat history yet</div>
        </div>

        {/* Bottom Actions */}
        <div className="p-3 border-t border-gray-200">
          <button
            onClick={() => router.push('/login')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:bg-gray-100 rounded-lg transition flex items-center gap-2"
          >
            <span>👤</span>
            <span>Switch Role</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-5xl mx-auto p-8">
          <div className="mb-8">
            <h1 className="text-4xl font-normal text-gray-900 mb-3">
              Frequently Asked Questions
            </h1>
            <p className="text-gray-600 text-lg">
              Professor-verified answers to common questions
            </p>
          </div>

          {loading ? (
            <div className="text-center py-20 text-gray-500">
              <div className="inline-block w-8 h-8 border-4 border-gray-300 border-t-orange-500 rounded-full animate-spin mb-4"></div>
              <p>Loading FAQ...</p>
            </div>
          ) : faqItems.length === 0 ? (
            <div className="text-center py-20">
              <div className="text-6xl mb-4">📚</div>
              <p className="text-gray-600 text-lg mb-2">No FAQ items yet</p>
              <p className="text-gray-500 text-sm">
                Your professor will add answers to common questions here
              </p>
            </div>
          ) : (
            <div className="space-y-3">
              {faqItems.map((item, index) => (
                <div
                  key={index}
                  className="bg-white rounded-xl border border-gray-200 overflow-hidden transition-all hover:border-gray-300"
                >
                  <button
                    onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                    className="w-full p-6 text-left flex items-start justify-between gap-4"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full font-medium">
                          ✓ Professor-Verified
                        </span>
                      </div>
                      <h3 className="text-lg font-medium text-gray-900">
                        {item.question}
                      </h3>
                    </div>
                    <svg
                      className={`w-5 h-5 text-gray-400 transition-transform flex-shrink-0 ${
                        expandedIndex === index ? 'rotate-180' : ''
                      }`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                  
                  {expandedIndex === index && (
                    <div className="px-6 pb-6 border-t border-gray-100">
                      <div className="pt-4 text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {item.answer}
                      </div>
                      <div className="mt-4 pt-4 border-t border-gray-100 text-xs text-gray-500">
                        Created by {item.created_by} on {new Date(item.created_at).toLocaleDateString()}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
