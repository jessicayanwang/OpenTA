'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle, HelpCircle, BookOpen, FileText, User } from 'lucide-react'
import Logo from '@/components/Logo'

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

        {/* Navigation - Compact */}
        <nav className="px-3 py-2 space-y-0.5">
          <button
            onClick={() => router.push('/faq')}
            className="w-full px-3 py-2 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <HelpCircle size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>FAQ</span>
          </button>
          <button
            onClick={() => router.push('/study-plan')}
            className="w-full px-3 py-2 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <BookOpen size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Study Plan</span>
          </button>
          <button
            onClick={() => router.push('/assignment-help')}
            className="w-full px-3 py-2 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
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
                  className={`rounded-xl border overflow-hidden transition-all ${
                    index % 3 === 0 ? 'bg-blue-50/30 border-blue-100 hover:border-blue-200' :
                    index % 3 === 1 ? 'bg-orange-50/30 border-orange-100 hover:border-orange-200' :
                    'bg-green-50/30 border-green-100 hover:border-green-200'
                  }`}
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
