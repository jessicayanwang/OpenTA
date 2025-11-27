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
      
      // Add mock FAQ items from professor's answered clusters
      const mockFAQs: FAQItem[] = [
        {
          question: 'How do I allocate memory with malloc?',
          answer: 'Memory allocation in C uses malloc() to dynamically allocate memory on the heap. You need to include <stdlib.h> and remember to free the memory when done to avoid memory leaks.',
          created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
          created_by: 'Professor'
        },
        {
          question: 'What is the difference between arrays and pointers?',
          answer: 'Arrays and pointers are closely related in C. An array name is essentially a pointer to the first element. However, arrays have fixed size and pointers can be reassigned.',
          created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          created_by: 'Professor'
        },
        {
          question: 'How do I debug segmentation faults?',
          answer: 'Segmentation faults occur when you access memory you shouldn\'t. Use valgrind to detect memory errors, check array bounds, ensure pointers are initialized, and verify malloc succeeded.',
          created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
          created_by: 'Professor'
        }
      ]
      
      setFaqItems([...mockFAQs, ...(data.faq || [])])
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
            <span>Self-study Room</span>
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
        <div className="max-w-4xl mx-auto p-6">
          <div className="mb-4">
            <h1 className="text-3xl font-normal text-gray-900 mb-1">
              Frequently Asked Questions
            </h1>
            <p className="text-gray-600 text-sm">
              Professor-verified answers to common questions
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12 text-gray-500">
              <div className="inline-block w-6 h-6 border-4 border-gray-300 border-t-orange-500 rounded-full animate-spin mb-3"></div>
              <p className="text-sm">Loading FAQ...</p>
            </div>
          ) : faqItems.length === 0 ? (
            <div className="text-center py-12">
              <div className="text-5xl mb-3">📚</div>
              <p className="text-gray-600 mb-1">No FAQ items yet</p>
              <p className="text-gray-500 text-sm">
                Your professor will add answers to common questions here
              </p>
            </div>
          ) : (
            <div className="space-y-2">
              {faqItems.map((item, index) => (
                <div
                  key={index}
                  className={`rounded-2xl border overflow-hidden transition-all ${
                    index % 3 === 0 ? 'bg-blue-50/30 border-blue-100 hover:border-blue-200' :
                    index % 3 === 1 ? 'bg-orange-50/30 border-orange-100 hover:border-orange-200' :
                    'bg-green-50/30 border-green-100 hover:border-green-200'
                  }`}
                >
                  <button
                    onClick={() => setExpandedIndex(expandedIndex === index ? null : index)}
                    className="w-full p-4 text-left flex items-start justify-between gap-3"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1.5">
                        <span className="bg-green-100 text-green-800 text-xs px-2 py-0.5 rounded-full font-medium">
                          ✓ Professor-Verified
                        </span>
                      </div>
                      <h3 className="text-base font-semibold text-gray-900">
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
                    <div className="px-4 pb-4 border-t border-gray-100">
                      <div className="pt-3 text-sm text-gray-700 whitespace-pre-wrap leading-relaxed">
                        {item.answer}
                      </div>
                      <div className="mt-3 pt-3 border-t border-gray-100 text-xs text-gray-500">
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
