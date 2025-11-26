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
            className="bg-white rounded-2xl border border-gray-200 p-10 hover:border-gray-300 hover:shadow-lg transition-all text-left group"
          >
            <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-blue-100 transition">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              Student Workspace
            </h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Ask questions, get help with assignments, and access personalized study plans
            </p>
            <div className="flex items-center text-gray-900 font-medium group-hover:gap-2 transition-all">
              Continue as Student
              <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
            </div>
          </button>

          {/* Professor Login */}
          <button
            onClick={() => handleRoleSelect('professor')}
            className="bg-white rounded-2xl border border-gray-200 p-10 hover:border-gray-300 hover:shadow-lg transition-all text-left group"
          >
            <div className="w-14 h-14 bg-orange-50 rounded-xl flex items-center justify-center mb-6 group-hover:bg-orange-100 transition">
              <svg className="w-8 h-8 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
              </svg>
            </div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-3">
              Professor Console
            </h2>
            <p className="text-gray-600 mb-6 leading-relaxed">
              Monitor student questions, create canonical answers, and manage course guardrails
            </p>
            <div className="flex items-center text-gray-900 font-medium group-hover:gap-2 transition-all">
              Continue as Professor
              <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
              </svg>
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
