'use client'

import { useRouter } from 'next/navigation'
import { MessageCircle, BookOpen, FileText, Users, ArrowRight, Sparkles, Shield, BarChart3, CheckCircle2 } from 'lucide-react'

export default function Home() {
  const router = useRouter()

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f7f7f5] via-[#fef9f2] to-[#fff5e8]">
      {/* Navigation */}
      <nav className="border-b border-[#E9E4DE] bg-white/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg">
              O
            </div>
            <span className="font-serif font-semibold text-xl text-[#1F1D20]">OpenTA</span>
          </div>
          <button
            onClick={() => router.push('/login')}
            className="px-6 py-2.5 bg-orange-600 hover:bg-orange-700 text-white font-medium text-sm rounded-xl shadow-sm hover:shadow-md transition-all duration-150 flex items-center gap-2"
          >
            Get Started
            <ArrowRight size={16} />
          </button>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-6 py-20">
        <div className="text-center max-w-4xl mx-auto mb-16">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-orange-100 border border-orange-200 rounded-full text-orange-700 text-sm font-medium mb-8">
            <Sparkles size={16} />
            AI-Powered Teaching Assistant
          </div>
          <h1 className="font-serif font-bold text-6xl tracking-tight text-[#1F1D20] mb-6 leading-tight">
            Empower Your Students with
            <span className="bg-gradient-to-r from-orange-500 to-orange-600 bg-clip-text text-transparent"> Intelligent Support</span>
          </h1>
          <p className="text-xl text-[#6F6B65] leading-relaxed mb-10">
            OpenTA combines AI agents with professor oversight to provide 24/7 personalized learning support, 
            grounded answers with citations, and actionable insights for educators.
          </p>
          <div className="flex items-center justify-center gap-4">
            <button
              onClick={() => router.push('/login')}
              className="px-8 py-4 bg-orange-600 hover:bg-orange-700 text-white font-semibold text-base rounded-xl shadow-lg hover:shadow-xl transition-all duration-150 flex items-center gap-2"
            >
              Try Demo
              <ArrowRight size={18} />
            </button>
            <button
              onClick={() => {
                document.getElementById('how-it-works')?.scrollIntoView({ behavior: 'smooth' })
              }}
              className="px-8 py-4 bg-white border-2 border-[#E9E4DE] hover:border-[#D9D3CC] text-[#1F1D20] font-semibold text-base rounded-xl shadow-sm hover:shadow-md transition-all duration-150"
            >
              Learn How
            </button>
          </div>
        </div>

        {/* Feature Cards */}
        <div className="grid md:grid-cols-3 gap-6 mb-20">
          <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8 shadow-sm hover:shadow-lg transition-all">
            <div className="w-14 h-14 bg-blue-50 rounded-xl flex items-center justify-center mb-6">
              <MessageCircle className="text-blue-600" size={28} />
            </div>
            <h3 className="text-2xl font-semibold text-[#1F1D20] mb-3">Smart Q&A</h3>
            <p className="text-[#6F6B65] leading-relaxed">
              Get instant answers to course questions with citations from syllabus, assignments, and course materials.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8 shadow-sm hover:shadow-lg transition-all">
            <div className="w-14 h-14 bg-green-50 rounded-xl flex items-center justify-center mb-6">
              <BookOpen className="text-green-600" size={28} />
            </div>
            <h3 className="text-2xl font-semibold text-[#1F1D20] mb-3">Study Plans</h3>
            <p className="text-[#6F6B65] leading-relaxed">
              Personalized study schedules based on goals, time availability, and current knowledge level.
            </p>
          </div>

          <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8 shadow-sm hover:shadow-lg transition-all">
            <div className="w-14 h-14 bg-purple-50 rounded-xl flex items-center justify-center mb-6">
              <FileText className="text-purple-600" size={28} />
            </div>
            <h3 className="text-2xl font-semibold text-[#1F1D20] mb-3">Assignment Help</h3>
            <p className="text-[#6F6B65] leading-relaxed">
              Socratic method guidance that helps students learn without giving away answers.
            </p>
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="bg-white border-y border-[#E9E4DE] py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-serif font-bold text-5xl text-[#1F1D20] mb-4">How OpenTA Works</h2>
            <p className="text-xl text-[#6F6B65]">A seamless journey for students and professors</p>
          </div>

          {/* User Flow Diagram */}
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12 mb-16">
              {/* Student Flow */}
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-2xl p-8 border-2 border-blue-200">
                <div className="flex items-center gap-3 mb-6">
                  <Users className="text-blue-600" size={28} />
                  <h3 className="text-2xl font-semibold text-blue-900">Student Experience</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">1</div>
                    <div>
                      <div className="font-semibold text-blue-900">Ask Questions</div>
                      <div className="text-blue-700 text-sm">Type questions about course logistics or content</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">2</div>
                    <div>
                      <div className="font-semibold text-blue-900">Get AI Response</div>
                      <div className="text-blue-700 text-sm">Receive grounded answers with source citations</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">3</div>
                    <div>
                      <div className="font-semibold text-blue-900">Explore More</div>
                      <div className="text-blue-700 text-sm">Access study plans, FAQ, and assignment help</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">4</div>
                    <div>
                      <div className="font-semibold text-blue-900">Learn Effectively</div>
                      <div className="text-blue-700 text-sm">Build understanding with Socratic guidance</div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Professor Flow */}
              <div className="bg-gradient-to-br from-orange-50 to-orange-100 rounded-2xl p-8 border-2 border-orange-200">
                <div className="flex items-center gap-3 mb-6">
                  <Shield className="text-orange-600" size={28} />
                  <h3 className="text-2xl font-semibold text-orange-900">Professor Controls</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">1</div>
                    <div>
                      <div className="font-semibold text-orange-900">Monitor Questions</div>
                      <div className="text-orange-700 text-sm">View all student questions and AI responses</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">2</div>
                    <div>
                      <div className="font-semibold text-orange-900">Review Clusters</div>
                      <div className="text-orange-700 text-sm">See patterns in student confusion</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">3</div>
                    <div>
                      <div className="font-semibold text-orange-900">Create Answers</div>
                      <div className="text-orange-700 text-sm">Write canonical answers for common questions</div>
                    </div>
                  </div>
                  <div className="flex items-start gap-3">
                    <div className="w-8 h-8 bg-orange-600 text-white rounded-full flex items-center justify-center font-semibold text-sm flex-shrink-0">4</div>
                    <div>
                      <div className="font-semibold text-orange-900">Adjust Guardrails</div>
                      <div className="text-orange-700 text-sm">Control AI behavior for graded content</div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Technical Flow */}
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl p-8 border border-gray-200">
              <h3 className="text-xl font-semibold text-gray-900 mb-6 flex items-center gap-2">
                <BarChart3 size={24} />
                Behind the Scenes: Multi-Agent Architecture
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                <div className="bg-white rounded-xl p-4 border border-gray-200 text-center">
                  <div className="font-semibold text-sm text-gray-900 mb-1">Question</div>
                  <div className="text-xs text-gray-600">Student asks</div>
                </div>
                <div className="flex items-center justify-center">
                  <ArrowRight className="text-gray-400" size={20} />
                </div>
                <div className="bg-white rounded-xl p-4 border border-gray-200 text-center">
                  <div className="font-semibold text-sm text-gray-900 mb-1">Retrieval</div>
                  <div className="text-xs text-gray-600">Search docs</div>
                </div>
                <div className="flex items-center justify-center">
                  <ArrowRight className="text-gray-400" size={20} />
                </div>
                <div className="bg-white rounded-xl p-4 border border-gray-200 text-center">
                  <div className="font-semibold text-sm text-gray-900 mb-1">AI Agent</div>
                  <div className="text-xs text-gray-600">Generate answer</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Benefits */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="font-serif font-bold text-5xl text-[#1F1D20] mb-4">Why Choose OpenTA?</h2>
            <p className="text-xl text-[#6F6B65]">Built with both students and professors in mind</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8">
              <CheckCircle2 className="text-green-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-[#1F1D20] mb-3">Grounded in Course Materials</h3>
              <p className="text-[#6F6B65] leading-relaxed">
                Every answer is backed by citations from your syllabus, assignments, and lecture notes. No hallucinations.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8">
              <CheckCircle2 className="text-green-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-[#1F1D20] mb-3">Professor Oversight</h3>
              <p className="text-[#6F6B65] leading-relaxed">
                Review question clusters, create verified answers, and control AI behavior for graded assignments.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8">
              <CheckCircle2 className="text-green-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-[#1F1D20] mb-3">24/7 Availability</h3>
              <p className="text-[#6F6B65] leading-relaxed">
                Students get instant help anytime, reducing bottlenecks during office hours and exam periods.
              </p>
            </div>

            <div className="bg-white rounded-2xl border border-[#E9E4DE] p-8">
              <CheckCircle2 className="text-green-600 mb-4" size={32} />
              <h3 className="text-xl font-semibold text-[#1F1D20] mb-3">Actionable Analytics</h3>
              <p className="text-[#6F6B65] leading-relaxed">
                Identify struggling students, content gaps, and common confusion points to improve your course.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-gradient-to-br from-orange-600 to-orange-700 py-20">
        <div className="max-w-4xl mx-auto px-6 text-center">
          <h2 className="font-serif font-bold text-5xl text-white mb-6">Ready to Transform Your Course?</h2>
          <p className="text-xl text-orange-100 mb-10 leading-relaxed">
            Try our demo to experience OpenTA as both a student and professor.
          </p>
          <button
            onClick={() => router.push('/login')}
            className="px-10 py-4 bg-white text-orange-600 font-bold text-lg rounded-xl shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-150 inline-flex items-center gap-3"
          >
            Start Demo Now
            <ArrowRight size={20} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-[#E9E4DE] bg-white py-8">
        <div className="max-w-7xl mx-auto px-6 text-center text-sm text-[#6F6B65]">
          <p>OpenTA - AI Teaching Assistant with Professor Controls • Built with FastAPI & Next.js</p>
        </div>
      </footer>
    </div>
  )
}
