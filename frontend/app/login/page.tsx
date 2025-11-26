'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Logo from '@/components/Logo'

export default function LoginPage() {
  const router = useRouter()

  const handleRoleSelect = (role: 'student' | 'professor') => {
    // In a real app, this would set auth state
    localStorage.setItem('userRole', role)
    localStorage.setItem('userId', role === 'student' ? 'student1' : 'prof1')
    
    // Navigate to appropriate workspace
    if (role === 'student') {
      router.push('/student')
    } else {
      router.push('/professor')
    }
  }

  return (
    <main className="min-h-screen bg-[#f7f7f5] flex items-center justify-center p-6">
      <div className="max-w-4xl w-full">
        <div className="text-center mb-16">
          <div className="flex justify-center mb-6">
            <Logo size="xl" showText={false} />
          </div>
          <h1 className="text-5xl font-normal text-gray-900 mb-4">
            Welcome to OpenTA
          </h1>
          <p className="text-xl text-gray-600">
            AI Teaching Assistant with Professor Controls
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-12">
          {/* Student Login */}
          <button
            onClick={() => handleRoleSelect('student')}
            className="bg-white rounded-2xl border-2 border-blue-200 p-10 hover:border-blue-300 hover:shadow-xl transition-all text-left group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-blue-50 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-300"></div>
            <div className="relative z-10">
              <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-blue-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                Student Workspace
              </h2>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Get instant, citation-backed answers to your course questions
              </p>
              <ul className="space-y-2.5 mb-8">
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                  Ask questions anytime, anywhere
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                  Get personalized study plans
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-blue-500 rounded-full"></div>
                  Receive Socratic assignment help
                </li>
              </ul>
              <div className="flex items-center text-blue-600 font-semibold group-hover:gap-2 transition-all">
                Continue as Student
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </button>

          {/* Professor Login */}
          <button
            onClick={() => handleRoleSelect('professor')}
            className="bg-white rounded-2xl border-2 border-orange-200 p-10 hover:border-orange-300 hover:shadow-xl transition-all text-left group relative overflow-hidden"
          >
            <div className="absolute top-0 right-0 w-32 h-32 bg-orange-50 rounded-full -mr-16 -mt-16 group-hover:scale-150 transition-transform duration-300"></div>
            <div className="relative z-10">
              <div className="w-14 h-14 bg-gradient-to-br from-orange-500 to-orange-600 rounded-xl flex items-center justify-center mb-6 group-hover:scale-110 transition-transform shadow-lg">
                <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h2 className="text-2xl font-semibold text-gray-900 mb-3">
                Professor Console
              </h2>
              <p className="text-gray-600 mb-6 leading-relaxed">
                Monitor, control, and enhance your AI teaching assistant
              </p>
              <ul className="space-y-2.5 mb-8">
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                  Review question patterns & clusters
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                  Create verified canonical answers
                </li>
                <li className="flex items-center gap-2 text-sm text-gray-700">
                  <div className="w-1.5 h-1.5 bg-orange-500 rounded-full"></div>
                  Track student confusion & analytics
                </li>
              </ul>
              <div className="flex items-center text-orange-600 font-semibold group-hover:gap-2 transition-all">
                Continue as Professor
                <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </div>
            </div>
          </button>
        </div>

        <div className="text-center text-sm text-gray-500">
          <p>Demo Mode • Click either role to continue</p>
        </div>
      </div>
    </main>
  )
}
