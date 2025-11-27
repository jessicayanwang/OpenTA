'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { MessageCircle, HelpCircle, BookOpen, FileText, User, X, Bell, Calendar, Clock, Trophy, ChevronRight, CheckCircle, XCircle, History, ChevronLeft } from 'lucide-react'
import Logo from '@/components/Logo'

type QuizItem = {
  question_id: string
  topic: string
  subtopic: string
  question: string
  options: string[]
  difficulty: number
  source_citation: string
}

type QuizHistory = {
  date: string
  score: number
  total: number
  items: any[]
}

type ExamRunwayDay = {
  day_number: number
  date: string
  intensity: string
  focus_topics: string[]
  tasks: any[]
}

export default function StudyPlanPage() {
  const router = useRouter()
  const studentId = 'student1' // In production, get from auth
  
  // Quiz state
  const [currentQuiz, setCurrentQuiz] = useState<QuizItem[]>([])
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0)
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null)
  const [quizResults, setQuizResults] = useState<any[]>([])
  const [showResults, setShowResults] = useState(false)
  const [loading, setLoading] = useState(false)
  
  // History
  const [quizHistory, setQuizHistory] = useState<QuizHistory[]>([])
  const [showHistory, setShowHistory] = useState(false)
  const [viewingHistoryIndex, setViewingHistoryIndex] = useState<number | null>(null)
  const [viewingDate, setViewingDate] = useState<string | null>(null) // Track which date we're viewing
  const [calendarMonth, setCalendarMonth] = useState(new Date().getMonth())
  const [calendarYear, setCalendarYear] = useState(new Date().getFullYear())
  
  // Reminders
  const [showReminder, setShowReminder] = useState(true)
  const [examRunway, setExamRunway] = useState<ExamRunwayDay[] | null>(null)
  
  // View state
  const [activeView, setActiveView] = useState<'quiz' | 'chat' | 'exam-prep'>('quiz')
  
  // Load quiz on mount
  useEffect(() => {
    loadDailyQuiz()
    loadQuizHistory()
    checkExamRunway()
  }, [])
  
  const loadDailyQuiz = async () => {
    setLoading(true)
    setViewingHistoryIndex(null) // Close history view
    setViewingDate(null) // Close date view
    setShowHistory(false) // Hide history panel
    try {
      const res = await fetch(`http://localhost:8000/api/adaptive/daily-quiz?student_id=${studentId}&count=3`)
      const data = await res.json()
      setCurrentQuiz(data.items || [])
      setCurrentQuestionIndex(0)
      setSelectedAnswer(null)
      setShowResults(false)
      setQuizResults([])
    } catch (e) {
      console.error('Failed to load quiz:', e)
    } finally {
      setLoading(false)
    }
  }
  
  const loadQuizHistory = () => {
    // Load from localStorage
    const saved = localStorage.getItem(`quiz_history_${studentId}`)
    if (saved) {
      setQuizHistory(JSON.parse(saved))
    }
  }
  
  const checkExamRunway = async () => {
    try {
      const res = await fetch(`http://localhost:8000/api/adaptive/exam-runway`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          exam_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
          exam_type: 'midterm',
          hours_per_day: 2
        })
      })
      if (res.ok) {
        const data = await res.json()
        setExamRunway(data.daily_plan)
      }
    } catch (e) {
      console.error('Failed to check exam runway:', e)
    }
  }

  const submitAnswer = async () => {
    if (selectedAnswer === null) return
    
    const currentQuestion = currentQuiz[currentQuestionIndex]
    
    try {
      const res = await fetch('http://localhost:8000/api/adaptive/submit-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          student_id: studentId,
          question_id: currentQuestion.question_id,
          selected_index: selectedAnswer,
          response_time_seconds: 10
        })
      })
      const result = await res.json()
      const updatedResults = [...quizResults, result]
      setQuizResults(updatedResults)
      
      // Move to next question or show results
      if (currentQuestionIndex < currentQuiz.length - 1) {
        setTimeout(() => {
          setCurrentQuestionIndex(currentQuestionIndex + 1)
          setSelectedAnswer(null)
        }, 1000)
      } else {
        // Quiz complete - save immediately with updated results
        setTimeout(() => {
          setShowResults(true)
          saveQuizToHistory(updatedResults)
        }, 1000)
      }
    } catch (e) {
      console.error('Failed to submit answer:', e)
    }
  }
  
  const saveQuizToHistory = (results: any[]) => {
    const correct = results.filter(r => r.correct).length
    const newHistory: QuizHistory = {
      date: new Date().toISOString(),
      score: correct,
      total: currentQuiz.length,
      items: results
    }
    const updated = [newHistory, ...quizHistory].slice(0, 10) // Keep last 10
    setQuizHistory(updated)
    localStorage.setItem(`quiz_history_${studentId}`, JSON.stringify(updated))
    console.log('Quiz saved to history:', { correct, total: currentQuiz.length, results })
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

      {/* Floating Reminder */}
      {showReminder && (
        <div className="fixed bottom-4 right-4 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-2xl shadow-2xl p-4 max-w-xs z-50 animate-bounce-gentle">
          <button
            onClick={() => setShowReminder(false)}
            className="absolute top-2 right-2 text-white/80 hover:text-white"
          >
            <X size={18} />
          </button>
          <div className="flex items-start gap-3">
            <Bell size={28} className="flex-shrink-0 mt-1" />
            <div>
              <h3 className="font-bold text-base mb-1.5">Daily Quiz Ready! 📚</h3>
              <p className="text-xs text-white/90 mb-2">
                3 personalized questions based on your weak topics
              </p>
              {examRunway && (
                <p className="text-xs text-white/80 mb-2">
                  📅 Exam in 7 days - Stay on track!
                </p>
              )}
              <button
                onClick={() => {
                  setActiveView('quiz')
                  setShowReminder(false)
                }}
                className="bg-white text-orange-600 px-3 py-1.5 rounded-lg font-semibold text-sm hover:bg-orange-50 transition-all"
              >
                Start Quiz
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="flex-1 overflow-y-auto">
        <div className="max-w-4xl mx-auto p-6">
          {/* Header with History Toggle */}
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-3xl font-normal text-gray-900 mb-1">Daily Learning Hub</h1>
              <p className="text-sm text-gray-600">Adaptive quizzes, chatbot help, and exam prep</p>
            </div>
            {!showHistory && (
              <button
                onClick={() => {
                  setShowHistory(true)
                  // Reset to current month when opening
                  setCalendarMonth(new Date().getMonth())
                  setCalendarYear(new Date().getFullYear())
                }}
                className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-all"
              >
                <History size={20} />
                <span>Quiz History</span>
              </button>
            )}
          </div>

          {/* Quiz History Calendar */}
          {showHistory && viewingDate === null && !showResults && (
            <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold">Quiz History Calendar</h2>
                <div className="flex gap-2">
                  <button
                    onClick={() => {
                      setCalendarMonth(new Date().getMonth())
                      setCalendarYear(new Date().getFullYear())
                    }}
                    className="px-3 py-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-all font-medium text-sm"
                  >
                    Today
                  </button>
                  <button
                    onClick={() => setShowHistory(false)}
                    className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-all"
                  >
                    <X size={20} />
                    <span>Close</span>
                  </button>
                </div>
              </div>
              {quizHistory.length === 0 ? (
                <p className="text-gray-500 text-center py-8">No quiz history yet. Complete a quiz to see your progress!</p>
              ) : (
                <div>
                  {/* Month/Year Navigation */}
                  <div className="flex items-center justify-center gap-3 mb-3">
                    <button
                      onClick={() => {
                        if (calendarMonth === 0) {
                          setCalendarMonth(11)
                          setCalendarYear(calendarYear - 1)
                        } else {
                          setCalendarMonth(calendarMonth - 1)
                        }
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-all text-sm"
                    >
                      <ChevronLeft size={16} />
                      <span className="font-medium">
                        {new Date(calendarYear, calendarMonth - 1).toLocaleString('default', { month: 'short' })}
                      </span>
                    </button>
                    
                    <div className="px-4 py-1.5 bg-blue-50 text-blue-900 font-bold rounded-lg border-2 border-blue-200 text-sm">
                      {new Date(calendarYear, calendarMonth).toLocaleString('default', { month: 'long' })} {calendarYear}
                    </div>
                    
                    <button
                      onClick={() => {
                        if (calendarMonth === 11) {
                          setCalendarMonth(0)
                          setCalendarYear(calendarYear + 1)
                        } else {
                          setCalendarMonth(calendarMonth + 1)
                        }
                      }}
                      className="flex items-center gap-1 px-3 py-1.5 text-blue-600 hover:bg-blue-50 rounded-lg transition-all text-sm"
                    >
                      <span className="font-medium">
                        {new Date(calendarYear, calendarMonth + 1).toLocaleString('default', { month: 'short' })}
                      </span>
                      <ChevronRight size={16} />
                    </button>
                  </div>
                  
                  {/* Calendar Grid */}
                  <div className="grid grid-cols-7 gap-1 mb-1 max-w-md mx-auto">
                    {['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'].map(day => (
                      <div key={day} className="text-center text-xs font-semibold text-gray-600 py-0.5">
                        {day}
                      </div>
                    ))}
                  </div>
                  
                  {/* Calendar Days */}
                  <div className="grid grid-cols-7 gap-1 max-w-md mx-auto">
                    {(() => {
                      const today = new Date()
                      const firstDay = new Date(calendarYear, calendarMonth, 1)
                      const lastDay = new Date(calendarYear, calendarMonth + 1, 0)
                      const startPadding = firstDay.getDay()
                      const days = []
                      
                      // Group quizzes by date
                      const quizzesByDate: { [key: string]: QuizHistory[] } = {}
                      quizHistory.forEach(quiz => {
                        const date = new Date(quiz.date).toDateString()
                        if (!quizzesByDate[date]) quizzesByDate[date] = []
                        quizzesByDate[date].push(quiz)
                      })
                      
                      // Add padding for first week
                      for (let i = 0; i < startPadding; i++) {
                        days.push(<div key={`pad-${i}`} className="h-10" />)
                      }
                      
                      // Add days
                      for (let day = 1; day <= lastDay.getDate(); day++) {
                        const date = new Date(calendarYear, calendarMonth, day)
                        const dateStr = date.toDateString()
                        const dayQuizzes = quizzesByDate[dateStr] || []
                        const quizCount = dayQuizzes.length
                        // Calculate overall percentage (total correct / total answered)
                        const totalCorrect = dayQuizzes.reduce((sum, q) => sum + q.score, 0)
                        const totalAnswered = dayQuizzes.reduce((sum, q) => sum + q.items.length, 0)
                        const avgScore = totalAnswered > 0 ? totalCorrect / totalAnswered : 0
                        
                        // Color intensity based on quiz count
                        const bgColor = quizCount === 0 
                          ? 'bg-gray-50' 
                          : quizCount === 1 
                          ? 'bg-orange-100'
                          : quizCount === 2
                          ? 'bg-orange-300'
                          : 'bg-orange-500'
                        
                        const textColor = quizCount >= 3 ? 'text-white' : 'text-gray-900'
                        const isToday = date.toDateString() === today.toDateString()
                        
                        days.push(
                          <button
                            key={day}
                            onClick={() => {
                              if (quizCount > 0) {
                                // Set viewing date to show all quizzes from this day
                                setViewingDate(dateStr)
                                setViewingHistoryIndex(null)
                              }
                            }}
                            disabled={quizCount === 0}
                            className={`h-10 rounded-md flex flex-col items-center justify-center transition-all relative group text-sm ${bgColor} ${textColor} ${
                              isToday ? 'ring-1 ring-orange-600' : ''
                            } ${quizCount > 0 ? 'hover:scale-105 cursor-pointer' : 'cursor-default'}`}
                            title={quizCount > 0 ? `${quizCount} quiz${quizCount > 1 ? 'zes' : ''} - ${Math.round(avgScore * 100)}% avg` : ''}
                          >
                            <span className="font-medium leading-none">{day}</span>
                            {quizCount > 0 && (
                              <>
                                <span className="text-[11px] opacity-80 leading-none">{quizCount}</span>
                                {/* Tooltip on hover */}
                                <div className="absolute bottom-full mb-1.5 left-1/2 -translate-x-1/2 bg-gray-900 text-white px-2 py-1.5 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10">
                                  <div className="font-semibold">{Math.round(avgScore * 100)}% Avg</div>
                                  <div>{quizCount} quiz{quizCount > 1 ? 'zes' : ''}</div>
                                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-[3px] border-transparent border-t-gray-900" />
                                </div>
                              </>
                            )}
                          </button>
                        )
                      }
                      
                      return days
                    })()}
                  </div>
                  
                  {/* Legend */}
                  <div className="mt-2 flex items-center justify-center gap-2 text-xs text-gray-600">
                    <span>Less</span>
                    <div className="flex gap-0.5">
                      <div className="w-4 h-4 bg-gray-50 border border-gray-200 rounded-sm" />
                      <div className="w-4 h-4 bg-orange-100 rounded-sm" />
                      <div className="w-4 h-4 bg-orange-300 rounded-sm" />
                      <div className="w-4 h-4 bg-orange-500 rounded-sm" />
                    </div>
                    <span>More</span>
                  </div>
                </div>
              )}
            </div>
          )}
          
          {/* Historical Quiz Details View */}
          {viewingDate !== null && (() => {
            // Get all quizzes from the selected date
            const dateQuizzes = quizHistory.filter(q => 
              new Date(q.date).toDateString() === viewingDate
            )
            const totalScore = dateQuizzes.reduce((sum, q) => sum + q.score, 0)
            // Use actual items length instead of stored total
            const totalQuestions = dateQuizzes.reduce((sum, q) => sum + q.items.length, 0)
            
            return (
              <div className="bg-white rounded-xl border border-gray-200 p-4 mb-4">
                <button
                  onClick={() => setViewingDate(null)}
                  className="flex items-center gap-2 text-gray-600 hover:text-gray-900 mb-3 text-sm"
                >
                  <ChevronRight size={18} className="rotate-180" />
                  <span>Back to History</span>
                </button>
                
                <div className="text-center mb-4">
                  <h2 className="text-xl font-bold mb-1">
                    {new Date(viewingDate).toLocaleDateString()}
                  </h2>
                  <p className="text-lg text-gray-600">
                    {dateQuizzes.length} quiz{dateQuizzes.length > 1 ? 'zes' : ''} • 
                    Overall: {totalScore}/{totalQuestions} 
                    ({Math.round(totalScore / totalQuestions * 100)}%)
                  </p>
                </div>
                
                {/* Show each quiz */}
                <div className="space-y-4">
                  {dateQuizzes.map((quiz, quizIdx) => {
                    // Use actual items length instead of total if they differ
                    const actualTotal = quiz.items.length
                    const percentage = actualTotal > 0 ? Math.round(quiz.score / actualTotal * 100) : 0
                    
                    return (
                      <div key={quizIdx} className="border-2 border-gray-200 rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2 pb-2 border-b border-gray-200">
                          <span className="font-semibold text-sm text-gray-900">
                            Quiz {quizIdx + 1}
                          </span>
                          <span className={`text-sm font-medium ${
                            percentage >= 70 ? 'text-green-600' : 'text-orange-600'
                          }`}>
                            {quiz.score}/{actualTotal} ({percentage}%)
                          </span>
                        </div>
                      
                      <div className="space-y-2">
                        {quiz.items.map((result: any, idx: number) => (
                          <div key={idx} className={`p-2 rounded border ${
                            result.correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                          }`}>
                            <div className="flex items-start gap-2">
                              {result.correct ? (
                                <CheckCircle size={16} className="text-green-600 flex-shrink-0 mt-0.5" />
                              ) : (
                                <XCircle size={16} className="text-red-600 flex-shrink-0 mt-0.5" />
                              )}
                              <div className="flex-1">
                                <p className="font-medium text-xs text-gray-900 mb-0.5">Q{idx + 1}</p>
                                <p className="text-xs text-gray-600">{result.explanation || 'No explanation available'}</p>
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                    )
                  })}
                </div>
              </div>
            )
          })()}

          {/* Quiz Interface */}
          {!showResults && !showHistory && currentQuiz.length > 0 && viewingDate === null && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-lg p-4">
              {/* Progress Bar */}
              <div className="mb-3">
                <div className="flex justify-between text-xs text-gray-600 mb-1.5">
                  <span>Question {currentQuestionIndex + 1} of {currentQuiz.length}</span>
                  <span className="text-orange-600 font-medium">{currentQuiz[currentQuestionIndex].topic}</span>
                </div>
                <div className="w-full h-1 bg-gray-200 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-orange-500 to-pink-500 transition-all duration-300"
                    style={{ width: `${((currentQuestionIndex + 1) / currentQuiz.length) * 100}%` }}
                  />
                </div>
              </div>

              {/* Question */}
              <div className="mb-3">
                <h2 className="text-lg font-medium text-gray-900 mb-1.5">
                  {currentQuiz[currentQuestionIndex].question}
                </h2>
                <p className="text-xs text-gray-500">
                  📖 {currentQuiz[currentQuestionIndex].source_citation}
                </p>
              </div>

              {/* Options */}
              <div className="space-y-1.5 mb-3">
                {currentQuiz[currentQuestionIndex].options.map((option, idx) => (
                  <button
                    key={idx}
                    onClick={() => setSelectedAnswer(idx)}
                    className={`w-full px-3 py-2 text-left rounded-lg border-2 transition-all text-sm ${
                      selectedAnswer === idx
                        ? 'border-orange-500 bg-orange-50'
                        : 'border-gray-200 hover:border-gray-300 bg-white'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                        selectedAnswer === idx ? 'border-orange-500 bg-orange-500' : 'border-gray-300'
                      }`}>
                        {selectedAnswer === idx && <div className="w-2 h-2 bg-white rounded-full" />}
                      </div>
                      <span className="text-gray-800 leading-tight">{option}</span>
                    </div>
                  </button>
                ))}
              </div>

              {/* Submit Button */}
              <button
                onClick={submitAnswer}
                disabled={selectedAnswer === null}
                className="w-full py-2.5 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-lg font-semibold text-sm hover:from-orange-600 hover:to-pink-600 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all"
              >
                {currentQuestionIndex < currentQuiz.length - 1 ? 'Next Question' : 'Finish Quiz'}
              </button>
            </div>
          )}

          {/* Results Screen */}
          {showResults && !showHistory && viewingDate === null && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-lg p-5">
              <div className="text-center mb-5">
                <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-pink-500 rounded-full flex items-center justify-center mx-auto mb-3">
                  <Trophy size={40} className="text-white" />
                </div>
                <h2 className="text-2xl font-bold text-gray-900 mb-2">Quiz Complete!</h2>
                <p className="text-lg text-gray-600">
                  You scored {quizResults.filter(r => r.correct).length} out of {currentQuiz.length}
                </p>
              </div>

              {/* Results Breakdown */}
              <div className="space-y-2 mb-5">
                {quizResults.map((result, idx) => (
                  <div key={idx} className={`p-3 rounded-lg border-2 ${
                    result.correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'
                  }`}>
                    <div className="flex items-start gap-2">
                      {result.correct ? (
                        <CheckCircle size={20} className="text-green-600 flex-shrink-0" />
                      ) : (
                        <XCircle size={20} className="text-red-600 flex-shrink-0" />
                      )}
                      <div className="flex-1">
                        <p className="font-medium text-sm text-gray-900 mb-1">{currentQuiz[idx].question}</p>
                        <p className="text-xs text-gray-600">{result.explanation}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Actions */}
              <div className="flex gap-4">
                <button
                  onClick={loadDailyQuiz}
                  className="flex-1 py-3 bg-gradient-to-r from-orange-500 to-pink-500 text-white rounded-lg font-semibold hover:from-orange-600 hover:to-pink-600 transition-all"
                >
                  Take Another Quiz
                </button>
                <button
                  onClick={() => router.push('/student')}
                  className="flex-1 py-3 bg-white border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-all"
                >
                  Back to Chat
                </button>
              </div>
            </div>
          )}

          {/* Loading State */}
          {loading && !showHistory && viewingDate === null && (
            <div className="bg-white rounded-xl border border-gray-200 shadow-lg p-10 text-center">
              <div className="animate-spin w-10 h-10 border-4 border-orange-500 border-t-transparent rounded-full mx-auto mb-3" />
              <p className="text-sm text-gray-600">Generating your personalized quiz...</p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
