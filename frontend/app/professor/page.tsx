'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { BarChart3, Users, Search, MessageSquare, User, UserCircle, AlertCircle, AlertTriangle, TrendingUp, FileText, Upload, Link, X, CheckCircle, Clock, Eye, Edit, Trash2 } from 'lucide-react'
import Logo from '@/components/Logo'

interface DashboardMetrics {
  total_questions: number
  avg_confidence: number
  struggling_students: number
  unresolved_items: number
}

interface TopicCount {
  topic: string
  count: number
}

interface RecentActivity {
  question: string
  student_id: string
  confidence: number
  timestamp: string
  artifact: string
}

interface Student {
  student_id: string
  questions_asked: number
  avg_confidence: number
  confusion_signals: number
  last_active: string | null
  topics: string[]
  status: 'struggling' | 'active' | 'thriving' | 'silent'
}

interface ContentGap {
  topic: string
  question_count: number
  example_questions: string[]
  suggested_action: string
  priority: 'high' | 'medium' | 'low'
}

interface QuestionCluster {
  cluster_id: string
  representative_question: string
  similar_questions: string[]
  count: number
  artifact: string | null
  section: string | null
  canonical_answer_id: string | null
  canonical_answer?: string
  last_updated?: string
  created_at: string
  last_seen: string
}

export default function ProfessorConsole() {
  const router = useRouter()
  const [activeTab, setActiveTab] = useState<'dashboard' | 'students' | 'content-gaps' | 'clusters'>('dashboard')
  const [loading, setLoading] = useState(false)
  
  // Dashboard data
  const [metrics, setMetrics] = useState<DashboardMetrics | null>(null)
  const [topTopics, setTopTopics] = useState<TopicCount[]>([])
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([])
  
  // Student data
  const [students, setStudents] = useState<Student[]>([])
  
  // Content gaps
  const [contentGaps, setContentGaps] = useState<ContentGap[]>([])
  const [expandedGaps, setExpandedGaps] = useState<Set<number>>(new Set())
  const [selectedGap, setSelectedGap] = useState<ContentGap | null>(null)
  const [showUploadModal, setShowUploadModal] = useState(false)
  const [uploadGap, setUploadGap] = useState<ContentGap | null>(null)
  
  // Clusters
  const [clusters, setClusters] = useState<QuestionCluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<QuestionCluster | null>(null)
  const [canonicalAnswer, setCanonicalAnswer] = useState('')
  const [showAnswerModal, setShowAnswerModal] = useState(false)
  const [showViewAnswerModal, setShowViewAnswerModal] = useState(false)
  
  // Demo data seeded
  const [demoSeeded, setDemoSeeded] = useState(false)

  useEffect(() => {
    const role = localStorage.getItem('userRole')
    if (role !== 'professor') {
      router.push('/login')
      return
    }
    
    // Seed demo data on first load
    if (!demoSeeded) {
      seedDemoData()
    } else {
      loadData()
    }
  }, [activeTab, demoSeeded])

  const seedDemoData = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/professor/seed-demo-data', {
        method: 'POST'
      })
      await res.json()
      setDemoSeeded(true)
    } catch (error) {
      console.error('Error seeding demo data:', error)
    }
  }

  const loadData = async () => {
    setLoading(true)
    try {
      if (activeTab === 'dashboard') {
        const res = await fetch('http://localhost:8000/api/professor/dashboard?course_id=cs50&days=7')
        const data = await res.json()
        setMetrics(data.metrics)
        setTopTopics(data.top_confusion_topics)
        setRecentActivity(data.recent_activity)
      } else if (activeTab === 'students') {
        const res = await fetch('http://localhost:8000/api/professor/students?course_id=cs50')
        const data = await res.json()
        setStudents(data.students)
      } else if (activeTab === 'content-gaps') {
        const res = await fetch('http://localhost:8000/api/professor/content-gaps?course_id=cs50')
        const data = await res.json()
        // Add mock high priority gaps
        const highPriorityGaps = [
          {
            topic: 'Pointers and Memory Management',
            question_count: 42,
            priority: 'high',
            example_questions: [
              'How do pointers work in C?',
              'What is the difference between stack and heap?',
              'When should I use malloc vs calloc?'
            ],
            suggested_action: 'Add comprehensive tutorial on pointers with visual diagrams'
          },
          {
            topic: 'Recursion',
            question_count: 35,
            priority: 'high',
            example_questions: [
              'How does recursion work?',
              'What is a base case?',
              'How to debug recursive functions?'
            ],
            suggested_action: 'Create step-by-step recursion examples with call stack visualization'
          }
        ]
        
        // Add low priority gaps with smaller counts
        const lowPriorityGaps = [
          {
            topic: 'File I/O Operations',
            question_count: 12,
            priority: 'low',
            example_questions: [
              'How do I read from a file?',
              'What is the difference between r and rb mode?'
            ],
            suggested_action: 'Add tutorial on file handling basics'
          },
          {
            topic: 'String Formatting',
            question_count: 8,
            priority: 'low',
            example_questions: [
              'How to use f-strings?',
              'What is the % operator for strings?'
            ],
            suggested_action: 'Create examples for different formatting methods'
          },
          {
            topic: 'List Comprehensions',
            question_count: 15,
            priority: 'low',
            example_questions: [
              'How do list comprehensions work?',
              'Can I use if-else in list comprehension?'
            ],
            suggested_action: 'Add interactive examples and exercises'
          }
        ]
        
        // Filter backend data to only include reasonable question counts (5-50)
        const filteredGaps = (data.gaps || []).filter((gap: ContentGap) => 
          gap.question_count >= 5 && gap.question_count <= 50
        )
        
        setContentGaps([...highPriorityGaps, ...filteredGaps, ...lowPriorityGaps])
      } else if (activeTab === 'clusters') {
        const res = await fetch('http://localhost:8000/api/professor/clusters?course_id=cs50&semantic=true&min_count=2')
        const data = await res.json()
        
        // Use clusters directly from backend - they have canonical_answer_id field
        // that determines if they're answered or not
        setClusters(data)
      }
    } catch (error) {
      console.error('Error loading data:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateAnswer = (cluster: QuestionCluster) => {
    setSelectedCluster(cluster)
    setCanonicalAnswer('')
    setShowAnswerModal(true)
  }

  const handleDeleteCluster = async (clusterId: string, e: React.MouseEvent) => {
    e.stopPropagation() // Prevent card click
    
    if (!confirm('Are you sure you want to delete this question cluster? This action cannot be undone.')) {
      return
    }

    try {
      // Remove from local state
      setClusters(clusters.filter(c => c.cluster_id !== clusterId))
      
      // Optionally call backend to delete
      // await fetch(`http://localhost:8000/api/professor/clusters/${clusterId}`, {
      //   method: 'DELETE'
      // })
    } catch (error) {
      console.error('Error deleting cluster:', error)
    }
  }

  const handlePublishAnswer = async () => {
    if (!selectedCluster || !canonicalAnswer.trim()) return

    try {
      await fetch('http://localhost:8000/api/professor/canonical-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cluster_id: selectedCluster.cluster_id,
          question: selectedCluster.representative_question,
          answer_markdown: canonicalAnswer,
          citations: []
        })
      })
      
      setShowAnswerModal(false)
      setCanonicalAnswer('')
      setSelectedCluster(null)
      
      // Reload clusters
      loadData()
    } catch (error) {
      console.error('Error publishing answer:', error)
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'struggling': return 'bg-red-100 text-red-800'
      case 'thriving': return 'bg-green-100 text-green-800'
      case 'active': return 'bg-blue-100 text-blue-800'
      case 'silent': return 'bg-gray-100 text-gray-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600'
    if (confidence >= 0.6) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="flex h-screen bg-[#f7f7f5]">
      {/* Sidebar - Refined Academic Minimalist */}
      <aside className="w-56 bg-gray-50 border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="px-3 py-2 border-b border-gray-200">
          <Logo size="sm" showText={true} />
        </div>
        
        {/* Navigation */}
        <nav className="px-3 py-2 space-y-0.5">
          <button
            onClick={() => setActiveTab('dashboard')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-0 active:bg-transparent"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <BarChart3 size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Dashboard</span>
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-0 active:bg-transparent"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <Users size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Student Analytics</span>
          </button>
          <button
            onClick={() => setActiveTab('content-gaps')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-0 active:bg-transparent"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <Search size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Content Gaps</span>
          </button>
          <button
            onClick={() => setActiveTab('clusters')}
            className="w-full px-3 py-2 text-left text-sm text-gray-600 hover:text-gray-900 hover:font-semibold rounded-lg transition-all duration-200 flex items-center gap-2.5 group relative focus:outline-none focus:ring-0 active:bg-transparent"
          >
            <div className="absolute left-0 w-1 h-0 bg-orange-500 rounded-r group-hover:h-full transition-all duration-200"></div>
            <MessageSquare size={16} className="text-gray-500 group-hover:text-orange-500 transition-colors" />
            <span>Question Clusters</span>
          </button>
        </nav>

        {/* Spacer */}
        <div className="flex-1"></div>

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
        <div className="max-w-7xl mx-auto p-8">
          {loading ? (
            <div className="text-center py-20 text-gray-500">
              <div className="inline-block w-8 h-8 border-4 border-gray-300 border-t-orange-500 rounded-full animate-spin mb-4"></div>
              <p>Loading...</p>
            </div>
          ) : (
            <>
              {/* Dashboard Tab */}
              {activeTab === 'dashboard' && metrics && (
                <div>
                  <h1 className="text-3xl font-normal text-gray-900 mb-1">Dashboard Overview</h1>
                  <p className="text-gray-600 mb-4">Real-time insights into student engagement and learning progress</p>

                  {/* Metrics Cards - Consistent Color Palette */}
                  <div className="grid grid-cols-4 gap-3 mb-4">
                    <button 
                      onClick={() => setActiveTab('students')}
                      className="bg-gradient-to-br from-orange-50 to-white rounded-2xl border border-orange-100 p-5 hover:shadow-xl hover:scale-105 transition-all duration-300 text-left group cursor-pointer relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-20 h-20 bg-orange-500 opacity-5 rounded-full -mr-10 -mt-10"></div>
                      <div className="text-xs font-medium text-orange-600 mb-2 uppercase tracking-wide">Questions</div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">304</div>
                      <div className="text-xs text-green-600 font-medium flex items-center gap-1">
                        <span>↑ 12%</span>
                        <span className="text-gray-400">vs last week</span>
                      </div>
                    </button>
                    <button 
                      onClick={() => setActiveTab('students')}
                      className="bg-gradient-to-br from-gray-50 to-white rounded-2xl border border-gray-200 p-5 hover:shadow-xl hover:scale-105 transition-all duration-300 text-left group cursor-pointer relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-20 h-20 bg-gray-400 opacity-5 rounded-full -mr-10 -mt-10"></div>
                      <div className="text-xs font-medium text-gray-600 mb-2 uppercase tracking-wide">Confidence</div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">
                        {(metrics.avg_confidence * 100).toFixed(0)}%
                      </div>
                      <div className="text-xs text-gray-500 font-medium">Target: 75%</div>
                    </button>
                    <button 
                      onClick={() => setActiveTab('students')}
                      className="bg-gradient-to-br from-gray-50 to-white rounded-2xl border border-gray-200 p-5 hover:shadow-xl hover:scale-105 transition-all duration-300 text-left group cursor-pointer relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-20 h-20 bg-gray-400 opacity-5 rounded-full -mr-10 -mt-10"></div>
                      <div className="text-xs font-medium text-gray-600 mb-2 uppercase tracking-wide">At Risk</div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">{metrics.struggling_students}</div>
                      <div className="text-xs text-orange-600 font-medium group-hover:underline">View details →</div>
                    </button>
                    <button 
                      onClick={() => setActiveTab('content-gaps')}
                      className="bg-gradient-to-br from-gray-50 to-white rounded-2xl border border-gray-200 p-5 hover:shadow-xl hover:scale-105 transition-all duration-300 text-left group cursor-pointer relative overflow-hidden"
                    >
                      <div className="absolute top-0 right-0 w-20 h-20 bg-gray-400 opacity-5 rounded-full -mr-10 -mt-10"></div>
                      <div className="text-xs font-medium text-gray-600 mb-2 uppercase tracking-wide">Pending</div>
                      <div className="text-3xl font-bold text-gray-900 mb-1">{metrics.unresolved_items}</div>
                      <div className="text-xs text-orange-600 font-medium group-hover:underline">Review now →</div>
                    </button>
                  </div>

                  <div className="grid grid-cols-3 gap-3 mb-4">
                    {/* Activity Trend Chart */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Weekly Activity
                      </h3>
                      <div className="flex items-end justify-between gap-1.5 mt-4" style={{height: '112px'}}>
                        {[
                          { day: 'M', count: 42 },
                          { day: 'T', count: 58 },
                          { day: 'W', count: 51 },
                          { day: 'T', count: 67 },
                          { day: 'F', count: 45 },
                          { day: 'S', count: 23 },
                          { day: 'S', count: 18 }
                        ].map((item, i) => {
                          const maxCount = 67
                          const heightPx = Math.max(8, (item.count / maxCount) * 100)
                          return (
                            <button 
                              key={i} 
                              onClick={() => setActiveTab('students')}
                              className="flex-1 flex flex-col items-center gap-1 group relative cursor-pointer"
                            >
                              <div 
                                className="w-full bg-orange-500 rounded-t transition-all hover:bg-orange-600 hover:scale-110" 
                                style={{height: `${heightPx}px`}}
                              ></div>
                              <span className="text-xs text-gray-500 mt-1 group-hover:text-orange-600 group-hover:font-semibold transition-all">{item.day}</span>
                              <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-gray-900 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap pointer-events-none z-10">
                                {item.count} questions
                              </div>
                            </button>
                          )
                        })}
                      </div>
                    </div>

                    {/* Student Engagement */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Student Engagement
                      </h3>
                      <div className="space-y-1.5">
                        <button 
                          onClick={() => setActiveTab('students')}
                          className="w-full text-left group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-600 group-hover:text-green-700">Active</span>
                            <span className="text-xs font-semibold text-green-600">45 students</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden cursor-pointer">
                            <div className="bg-green-500 h-2 rounded-full transition-all duration-300 group-hover:bg-green-600" style={{width: '75%'}}></div>
                          </div>
                        </button>
                        <button 
                          onClick={() => setActiveTab('students')}
                          className="w-full text-left group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-600 group-hover:text-yellow-700">Moderate</span>
                            <span className="text-xs font-semibold text-yellow-600">12 students</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden cursor-pointer">
                            <div className="bg-yellow-500 h-2 rounded-full transition-all duration-300 group-hover:bg-yellow-600" style={{width: '20%'}}></div>
                          </div>
                        </button>
                        <button 
                          onClick={() => setActiveTab('students')}
                          className="w-full text-left group"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-xs text-gray-600 group-hover:text-red-700">At Risk</span>
                            <span className="text-xs font-semibold text-red-600">3 students</span>
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-2 overflow-hidden cursor-pointer">
                            <div className="bg-red-500 h-2 rounded-full transition-all duration-300 group-hover:bg-red-600 group-hover:animate-pulse" style={{width: '5%'}}></div>
                          </div>
                        </button>
                      </div>
                    </div>

                    {/* Quick Stats */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Quick Stats
                      </h3>
                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Avg Response Time</span>
                          <span className="text-sm font-semibold text-gray-900">2.3s</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Peak Hour</span>
                          <span className="text-sm font-semibold text-gray-900">2-4 PM</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Most Active Day</span>
                          <span className="text-sm font-semibold text-gray-900">Thursday</span>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-xs text-gray-600">Citations Used</span>
                          <span className="text-sm font-semibold text-gray-900">1,247</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3">
                    {/* Top Confusion Topics */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Top Confusion Topics
                      </h3>
                      {topTopics.length === 0 ? (
                        <p className="text-gray-500 text-sm">No confusion signals yet</p>
                      ) : (
                        <div className="space-y-3">
                          {topTopics.map((topic, i) => (
                            <div key={i} className="flex items-center justify-between">
                              <div className="flex-1">
                                <div className="text-sm font-medium text-gray-900">{topic.topic}</div>
                                <div className="w-full bg-gray-200 rounded-full h-2 mt-1">
                                  <div
                                    className="bg-red-500 h-2 rounded-full"
                                    style={{ width: `${(topic.count / topTopics[0].count) * 100}%` }}
                                  ></div>
                                </div>
                              </div>
                              <div className="ml-4 text-sm font-semibold text-gray-600">{topic.count}</div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>

                    {/* Recent Activity */}
                    <div className="bg-white rounded-2xl border border-gray-100 p-4 shadow-sm hover:shadow-md transition-shadow">
                      <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                        <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
                        Recent Activity
                      </h3>
                      {recentActivity.length === 0 ? (
                        <p className="text-gray-500 text-sm">No recent activity</p>
                      ) : (
                        <div className="space-y-3 max-h-96 overflow-y-auto">
                          {recentActivity.map((activity, i) => (
                            <div key={i} className="border-l-2 border-gray-300 pl-3 py-1">
                              <div className="text-xs text-gray-500 mb-1">
                                {activity.student_id} • {new Date(activity.timestamp).toLocaleTimeString()}
                              </div>
                              <div className="text-sm text-gray-900">{activity.question}</div>
                              <div className="flex items-center gap-2 mt-1">
                                <span className="text-xs text-gray-500">{activity.artifact}</span>
                                <span className={`text-xs font-medium ${getConfidenceColor(activity.confidence)}`}>
                                  {(activity.confidence * 100).toFixed(0)}% confidence
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Student Analytics Tab */}
              {activeTab === 'students' && (
                <div>
                  <h1 className="text-3xl font-normal text-gray-900 mb-1">Student Analytics</h1>
                  <p className="text-gray-600 mb-4">Individual student engagement and performance</p>

                  {students.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">No student data available</div>
                  ) : (
                    <div className="grid grid-cols-4 gap-3 p-4 bg-gradient-to-br from-orange-50/30 via-transparent to-blue-50/30 rounded-2xl">
                      {students.map((student, idx) => {
                        // Generate different soft avatar colors based on index
                        const avatarColors = [
                          'from-orange-200 to-orange-300',
                          'from-blue-200 to-blue-300',
                          'from-purple-200 to-purple-300',
                          'from-emerald-200 to-emerald-300',
                          'from-rose-200 to-rose-300',
                          'from-indigo-200 to-indigo-300'
                        ]
                        const iconColors = [
                          'text-orange-600',
                          'text-blue-600',
                          'text-purple-600',
                          'text-emerald-600',
                          'text-rose-600',
                          'text-indigo-600'
                        ]
                        const avatarColor = avatarColors[idx % avatarColors.length]
                        const iconColor = iconColors[idx % iconColors.length]
                        
                        return (
                          <button
                            key={student.student_id}
                            className="bg-white/60 backdrop-blur-md rounded-xl border border-white/40 shadow-lg p-4 hover:shadow-xl hover:bg-white/70 hover:border-orange-300/50 transition-all duration-300 text-left group"
                          >
                            {/* Header with Avatar */}
                            <div className="flex flex-col items-center mb-3">
                              <div className={`w-14 h-14 rounded-full bg-gradient-to-br ${avatarColor} bg-opacity-60 flex items-center justify-center shadow-sm mb-2 group-hover:scale-110 transition-transform backdrop-blur-sm`}>
                                <UserCircle className={`w-9 h-9 ${iconColor}`} strokeWidth={1.5} />
                              </div>
                              <h3 className="text-xs font-semibold text-gray-900 text-center group-hover:text-orange-600 transition-colors">
                                {student.student_id}
                              </h3>
                              <span className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium mt-1 ${getStatusColor(student.status)}`}>
                                {student.status}
                              </span>
                            </div>

                            {/* Stats - Compact */}
                            <div className="space-y-2 mb-3">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">Questions</span>
                                <span className="font-bold text-gray-900">{student.questions_asked}</span>
                              </div>
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">Confidence</span>
                                <span className={`font-bold ${getConfidenceColor(student.avg_confidence)}`}>
                                  {(student.avg_confidence * 100).toFixed(0)}%
                                </span>
                              </div>
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-gray-500">Signals</span>
                                <span className="font-bold text-red-600">{student.confusion_signals}</span>
                              </div>
                            </div>

                            {/* Topics - Compact */}
                            <div className="mb-3">
                              <div className="flex flex-wrap gap-1">
                                {student.topics.slice(0, 2).map((topic, i) => (
                                  <span key={i} className="text-xs bg-gray-50 text-gray-600 px-1.5 py-0.5 rounded">
                                    {topic}
                                  </span>
                                ))}
                                {student.topics.length > 2 && (
                                  <span className="text-xs text-gray-400">
                                    +{student.topics.length - 2}
                                  </span>
                                )}
                              </div>
                            </div>

                            {/* Footer - Compact */}
                            <div className="pt-2 border-t border-gray-100 text-center">
                              {student.status === 'struggling' ? (
                                <span className="text-xs text-orange-600 font-medium group-hover:underline">
                                  Intervene →
                                </span>
                              ) : (
                                <span className="text-xs text-gray-400">
                                  {student.last_active ? new Date(student.last_active).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) : 'Inactive'}
                                </span>
                              )}
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  )}
                </div>
              )}

              {/* Content Gaps Tab */}
              {activeTab === 'content-gaps' && (
                <div>
                  <h1 className="text-3xl font-normal text-gray-900 mb-1">Content Gap Analysis</h1>
                  <p className="text-gray-600 mb-4">Topics with low-confidence responses that may need more materials</p>

                  {contentGaps.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">No content gaps identified</div>
                  ) : (
                    <div className="grid grid-cols-4 gap-3 p-4 bg-gradient-to-br from-orange-50/30 via-transparent to-purple-50/30 rounded-2xl">
                      {contentGaps.map((gap, i) => {
                        const isHighPriority = gap.priority === 'high'
                        
                        // Irregular grid sizing - high priority slightly larger
                        const gridClass = isHighPriority 
                          ? 'col-span-2'
                          : 'col-span-1'
                        
                        return (
                          <button
                            key={i}
                            onClick={() => setSelectedGap(gap)}
                            className={`${gridClass} bg-white/60 backdrop-blur-md rounded-xl border border-white/40 shadow-lg p-4 hover:shadow-2xl hover:bg-white/75 hover:scale-[1.02] transition-all duration-300 text-left group relative overflow-hidden`}
                          >
                            {/* Priority Indicator Bar */}
                            <div className={`absolute left-0 top-0 bottom-0 w-1 ${
                              isHighPriority ? 'bg-gradient-to-b from-orange-400 to-orange-600' : 'bg-gradient-to-b from-gray-300 to-gray-400'
                            }`}></div>

                            {/* Animated Background Gradient */}
                            <div className={`absolute inset-0 opacity-0 group-hover:opacity-100 transition-opacity duration-500 ${
                              isHighPriority 
                                ? 'bg-gradient-to-br from-orange-50/50 to-transparent' 
                                : 'bg-gradient-to-br from-gray-50/50 to-transparent'
                            }`}></div>

                            {/* Header - Interactive */}
                            <div className="relative mb-3 ml-2">
                              <div className="flex items-start gap-2 mb-2">
                                <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 transition-all duration-300 group-hover:scale-110 ${
                                  isHighPriority ? 'bg-orange-100 group-hover:bg-orange-200' : 'bg-gray-100 group-hover:bg-gray-200'
                                }`}>
                                  {isHighPriority ? (
                                    <AlertCircle className="w-5 h-5 text-orange-600 group-hover:animate-pulse" />
                                  ) : (
                                    <AlertTriangle className="w-5 h-5 text-gray-600" />
                                  )}
                                </div>
                                <span className={`text-xs px-2 py-1 rounded-full font-medium transition-all group-hover:scale-105 ml-auto ${
                                  isHighPriority ? 'bg-orange-100 text-orange-700 group-hover:bg-orange-200' : 'bg-gray-100 text-gray-700 group-hover:bg-gray-200'
                                }`}>
                                  {gap.priority}
                                </span>
                              </div>
                              <h3 className={`font-semibold text-gray-900 group-hover:text-orange-600 transition-colors ${
                                isHighPriority ? 'text-base' : 'text-sm'
                              }`}>
                                {gap.topic}
                              </h3>
                            </div>

                            {/* Metrics - Better Formatted */}
                            <div className="relative grid grid-cols-2 gap-2 mb-3 ml-2">
                              <div className="bg-gray-50/80 rounded-lg p-2.5 transition-all hover:bg-gray-100/80">
                                <div className="text-xs text-gray-500 mb-1">Questions</div>
                                <div className="text-xl font-bold text-gray-900 mb-1">{gap.question_count}</div>
                                <div className="w-full bg-gray-200 rounded-full h-1.5">
                                  <div 
                                    className={`h-1.5 rounded-full transition-all ${isHighPriority ? 'bg-orange-500' : 'bg-gray-400'}`}
                                    style={{width: `${isHighPriority ? Math.min(100, (gap.question_count / 50) * 100) : Math.min(100, (gap.question_count / 20) * 100)}%`}}
                                  ></div>
                                </div>
                              </div>
                              <div className="bg-gray-50/80 rounded-lg p-2.5 transition-all hover:bg-gray-100/80 flex flex-col justify-between">
                                <div className="text-xs text-gray-500">Impact</div>
                                <div className="flex items-center justify-between">
                                  <div className={`text-xl font-bold ${isHighPriority ? 'text-orange-600' : 'text-gray-600'}`}>
                                    {isHighPriority ? 'High' : 'Low'}
                                  </div>
                                  <TrendingUp className={`w-5 h-5 ${isHighPriority ? 'text-orange-500' : 'text-gray-400'}`} />
                                </div>
                              </div>
                            </div>

                            {/* Footer - Click to View Details */}
                            <div className="mt-2 pt-1.5 border-t border-gray-200/50 flex items-center justify-between ml-2">
                              <span className="text-xs text-gray-400">
                                Click for details
                              </span>
                              <span className="text-xs text-orange-600 font-medium group-hover:underline">
                                View →
                              </span>
                            </div>
                          </button>
                        )
                      })}
                    </div>
                  )}

                  {/* Gap Details Modal */}
                  {selectedGap && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setSelectedGap(null)}>
                      <div className="bg-white rounded-2xl shadow-2xl max-w-xl w-full max-h-[85vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
                        <div className="overflow-y-auto max-h-[85vh] p-5 pr-4" style={{scrollbarGutter: 'stable'}}>
                        {/* Header - Compact */}
                        <div className="flex items-start justify-between mb-4">
                          <div className="flex items-center gap-2">
                            <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                              selectedGap.priority === 'high' ? 'bg-orange-100' : 'bg-gray-100'
                            }`}>
                              {selectedGap.priority === 'high' ? (
                                <AlertCircle className="w-5 h-5 text-orange-600" />
                              ) : (
                                <AlertTriangle className="w-5 h-5 text-gray-600" />
                              )}
                            </div>
                            <div>
                              <h2 className="text-xl font-bold text-gray-900">{selectedGap.topic}</h2>
                              <span className={`inline-block text-xs px-2 py-0.5 rounded-full font-medium ${
                                selectedGap.priority === 'high' ? 'bg-orange-100 text-orange-700' : 'bg-gray-100 text-gray-700'
                              }`}>
                                {selectedGap.priority} priority
                              </span>
                            </div>
                          </div>
                          <button onClick={() => setSelectedGap(null)} className="text-gray-400 hover:text-gray-600 transition-colors">
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                            </svg>
                          </button>
                        </div>

                        {/* Metrics - Compact */}
                        <div className="grid grid-cols-2 gap-3 mb-4">
                          <div className="bg-gray-50 rounded-2xl p-3">
                            <div className="text-xs text-gray-500 mb-1">Questions</div>
                            <div className="text-2xl font-bold text-gray-900">{selectedGap.question_count}</div>
                          </div>
                          <div className="bg-gray-50 rounded-2xl p-3">
                            <div className="text-xs text-gray-500 mb-1">Impact</div>
                            <div className={`text-2xl font-bold ${selectedGap.priority === 'high' ? 'text-orange-600' : 'text-gray-600'}`}>
                              {selectedGap.priority === 'high' ? 'High' : 'Low'}
                            </div>
                          </div>
                        </div>

                        {/* Example Questions - Compact */}
                        <div className="mb-4">
                          <h3 className="text-sm font-semibold text-gray-900 mb-2 flex items-center gap-1.5">
                            <FileText className="w-4 h-4" />
                            Example Questions
                          </h3>
                          <div className="space-y-2">
                            {selectedGap.example_questions.map((q, j) => (
                              <div key={j} className="bg-gray-50 rounded-2xl p-2.5 text-sm text-gray-700 border-l-4 border-orange-300">
                                {q}
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Suggested Action - Compact */}
                        <div className="bg-orange-50 rounded-2xl p-3 border border-orange-200 mb-4">
                          <h3 className="text-xs font-semibold text-orange-900 mb-1.5">💡 Suggested Action</h3>
                          <p className="text-sm text-gray-700">{selectedGap.suggested_action}</p>
                        </div>

                        {/* Action Buttons - Compact */}
                        <div className="flex gap-2">
                          <button 
                            onClick={() => {
                              setUploadGap(selectedGap)
                              setShowUploadModal(true)
                            }}
                            className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white px-4 py-2.5 rounded-2xl font-medium hover:shadow-lg transition-all text-sm flex items-center justify-center gap-2"
                          >
                            <Upload className="w-4 h-4" />
                            Upload Material
                          </button>
                          <button onClick={() => setSelectedGap(null)} className="px-4 py-2.5 border border-gray-300 rounded-2xl font-medium text-gray-700 hover:bg-gray-50 transition-all text-sm">
                            Close
                          </button>
                        </div>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Upload Material Modal */}
                  {showUploadModal && uploadGap && (
                    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setShowUploadModal(false)}>
                      <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full overflow-hidden" onClick={(e) => e.stopPropagation()}>
                        <div className="p-6">
                          {/* Header */}
                          <div className="flex items-start justify-between mb-4">
                            <div>
                              <h2 className="text-xl font-bold text-gray-900 mb-1">Upload Learning Material</h2>
                              <p className="text-sm text-gray-600">For: <span className="font-semibold text-orange-600">{uploadGap.topic}</span></p>
                            </div>
                            <button onClick={() => setShowUploadModal(false)} className="text-gray-400 hover:text-gray-600 transition-colors">
                              <X className="w-5 h-5" />
                            </button>
                          </div>

                          {/* Upload Options */}
                          <div className="space-y-3 mb-6">
                            {/* File Upload */}
                            <div className="border-2 border-dashed border-gray-300 rounded-2xl p-6 hover:border-orange-400 hover:bg-orange-50/50 transition-all cursor-pointer group">
                              <label className="cursor-pointer flex flex-col items-center">
                                <div className="w-12 h-12 rounded-full bg-orange-100 flex items-center justify-center mb-3 group-hover:bg-orange-200 transition-colors">
                                  <Upload className="w-6 h-6 text-orange-600" />
                                </div>
                                <div className="text-center">
                                  <p className="text-sm font-semibold text-gray-900 mb-1">Upload Files</p>
                                  <p className="text-xs text-gray-500">PDF, DOCX, TXT, or Markdown</p>
                                </div>
                                <input type="file" className="hidden" accept=".pdf,.docx,.txt,.md" multiple />
                              </label>
                            </div>

                            {/* Link Input */}
                            <div className="border-2 border-gray-200 rounded-2xl p-4 hover:border-orange-400 hover:bg-orange-50/50 transition-all">
                              <div className="flex items-center gap-3 mb-2">
                                <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                                  <Link className="w-5 h-5 text-blue-600" />
                                </div>
                                <div className="flex-1">
                                  <p className="text-sm font-semibold text-gray-900">Add Resource Link</p>
                                  <p className="text-xs text-gray-500">External documentation or tutorial</p>
                                </div>
                              </div>
                              <input 
                                type="url" 
                                placeholder="https://example.com/tutorial" 
                                className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent"
                              />
                            </div>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex gap-3">
                            <button className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white px-4 py-2.5 rounded-2xl font-medium hover:shadow-lg transition-all text-sm">
                              Submit Materials
                            </button>
                            <button onClick={() => setShowUploadModal(false)} className="px-4 py-2.5 border border-gray-300 rounded-2xl font-medium text-gray-700 hover:bg-gray-50 transition-all text-sm">
                              Cancel
                            </button>
                          </div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Clusters Tab */}
              {activeTab === 'clusters' && (
                <div>
                  <h1 className="text-3xl font-normal text-gray-900 mb-1">Question Clusters</h1>
                  <p className="text-gray-600 mb-4">AI-powered semantic grouping of similar questions</p>

                  {clusters.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">
                      <p>No question clusters yet</p>
                      <p className="text-sm mt-2">Students need to ask questions first</p>
                    </div>
                  ) : (
                    <>
                      {/* Summary Stats */}
                      <div className="grid grid-cols-2 gap-3 mb-4">
                        <div className="bg-gradient-to-br from-green-50 to-white rounded-2xl border border-green-100 p-4">
                          <div className="flex items-center gap-2 mb-1">
                            <CheckCircle className="w-5 h-5 text-green-600" />
                            <span className="text-sm font-medium text-green-700">Answered</span>
                          </div>
                          <div className="text-2xl font-bold text-gray-900">
                            {clusters.filter(c => c.canonical_answer_id).length}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {clusters.filter(c => c.canonical_answer_id).reduce((sum, c) => sum + c.count, 0)} questions covered
                          </div>
                        </div>
                        <div className="bg-gradient-to-br from-orange-50 to-white rounded-2xl border border-orange-100 p-4">
                          <div className="flex items-center gap-2 mb-1">
                            <Clock className="w-5 h-5 text-orange-600" />
                            <span className="text-sm font-medium text-orange-700">Needs Answer</span>
                          </div>
                          <div className="text-2xl font-bold text-gray-900">
                            {clusters.filter(c => !c.canonical_answer_id).length}
                          </div>
                          <div className="text-xs text-gray-500 mt-1">
                            {clusters.filter(c => !c.canonical_answer_id).reduce((sum, c) => sum + c.count, 0)} questions waiting
                          </div>
                        </div>
                      </div>

                      {/* Side-by-Side Columns */}
                      <div className="grid grid-cols-2 gap-4">
                        {/* Answered Clusters */}
                        <div>
                          <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <CheckCircle className="w-5 h-5 text-green-600" />
                            Answered Clusters
                          </h2>
                          <div className="space-y-3">
                            {clusters.filter(c => c.canonical_answer_id).map((cluster) => (
                              <div key={cluster.cluster_id} className="relative group/card">
                                <button
                                  onClick={() => {
                                    setSelectedCluster(cluster)
                                    setShowViewAnswerModal(true)
                                  }}
                                  className="bg-white/60 backdrop-blur-md rounded-2xl border border-green-200 p-4 hover:shadow-lg hover:border-green-300 transition-all text-left group w-full"
                                >
                                  <div className="flex items-center gap-2 mb-2">
                                    <CheckCircle className="w-4 h-4 text-green-600" />
                                    <span className="text-xs font-medium text-green-700">{cluster.count} questions</span>
                                    {cluster.artifact && (
                                      <span className="text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full">
                                        {cluster.artifact}
                                      </span>
                                    )}
                                  </div>
                                <h3 className="text-sm font-semibold text-gray-900 mb-2 group-hover:text-green-600 transition-colors">
                                  {cluster.representative_question}
                                </h3>
                                <p className="text-xs text-gray-600 line-clamp-2 mb-2">
                                  {cluster.canonical_answer}
                                </p>
                                <div className="flex items-center justify-between text-xs">
                                  <span className="text-gray-400">{cluster.last_updated}</span>
                                  <span className="text-green-600 font-medium group-hover:underline flex items-center gap-1">
                                    <Eye className="w-3 h-3" />
                                    View Answer
                                  </span>
                                </div>
                              </button>
                              <button
                                onClick={(e) => handleDeleteCluster(cluster.cluster_id, e)}
                                className="absolute top-2 right-2 p-1.5 bg-red-50 text-red-600 rounded-lg opacity-0 group-hover/card:opacity-100 hover:bg-red-100 transition-all"
                                title="Delete cluster"
                              >
                                <Trash2 className="w-3.5 h-3.5" />
                              </button>
                            </div>
                            ))}
                          </div>
                        </div>

                        {/* Unanswered Clusters */}
                        <div>
                          <h2 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-orange-600" />
                            Needs Answer
                          </h2>
                          <div className="space-y-3">
                            {clusters.filter(c => !c.canonical_answer_id).map((cluster) => (
                              <div key={cluster.cluster_id} className="relative group/card">
                                <button
                                  onClick={() => handleCreateAnswer(cluster)}
                                  className="bg-white/60 backdrop-blur-md rounded-2xl border border-orange-200 p-4 hover:shadow-lg hover:border-orange-300 transition-all text-left group w-full"
                                >
                                  <div className="flex items-center gap-2 mb-2">
                                    <Clock className="w-4 h-4 text-orange-600" />
                                    <span className="text-xs font-medium text-orange-700">{cluster.count} questions</span>
                                    {cluster.artifact && (
                                      <span className="text-xs bg-purple-50 text-purple-700 px-2 py-0.5 rounded-full">
                                        {cluster.artifact}
                                      </span>
                                    )}
                                  </div>
                                  <h3 className="text-sm font-semibold text-gray-900 mb-2 group-hover:text-orange-600 transition-colors">
                                    {cluster.representative_question}
                                  </h3>
                                  <p className="text-xs text-gray-500 mb-2">
                                    {cluster.count} students waiting for answer
                                  </p>
                                  <div className="flex items-center justify-between text-xs">
                                    <span className="text-gray-400">No answer yet</span>
                                    <span className="text-orange-600 font-medium group-hover:underline flex items-center gap-1">
                                      <Edit className="w-3 h-3" />
                                      Create Answer
                                    </span>
                                  </div>
                                </button>
                                <button
                                  onClick={(e) => handleDeleteCluster(cluster.cluster_id, e)}
                                  className="absolute top-2 right-2 p-1.5 bg-red-50 text-red-600 rounded-lg opacity-0 group-hover/card:opacity-100 hover:bg-red-100 transition-all"
                                  title="Delete cluster"
                                >
                                  <Trash2 className="w-3.5 h-3.5" />
                                </button>
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Canonical Answer Modal */}
      {showAnswerModal && selectedCluster && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center p-4 z-50" onClick={() => {
          setShowAnswerModal(false)
          setSelectedCluster(null)
          setCanonicalAnswer('')
        }}>
          <div className="bg-white rounded-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="overflow-y-auto max-h-[85vh]">
            <div className="p-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900">Create Canonical Answer</h2>
              <p className="text-xs text-gray-600 mt-1">
                This answer will automatically respond to similar questions
              </p>
            </div>
            
            <div className="p-4">
              <div className="mb-3">
                <div className="text-xs font-semibold text-gray-700 mb-1.5">Representative Question:</div>
                <div className="bg-gray-50 p-2.5 rounded-xl text-sm text-gray-900">
                  {selectedCluster.representative_question}
                </div>
              </div>

              <div className="mb-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full font-medium">
                    {selectedCluster.count} similar questions
                  </span>
                  {selectedCluster.artifact && (
                    <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded-full">
                      {selectedCluster.artifact}
                    </span>
                  )}
                </div>
              </div>

              <div className="mb-3">
                <label className="block text-xs font-semibold text-gray-700 mb-1.5">
                  Canonical Answer (Markdown supported)
                </label>
                <textarea
                  value={canonicalAnswer}
                  onChange={(e) => setCanonicalAnswer(e.target.value)}
                  className="w-full h-48 px-3 py-2 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 font-mono text-sm"
                  placeholder="Write a comprehensive answer that will help all students asking similar questions...

You can use markdown:
- **bold** for emphasis
- `code` for code snippets
- Lists and formatting"
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-xl p-2.5 mb-3">
                <div className="text-xs font-semibold text-blue-900 mb-1">💡 Tip:</div>
                <div className="text-xs text-blue-800">
                  Write a clear, comprehensive answer that addresses the core question. This will be shown to all students asking similar questions in the future.
                </div>
              </div>
            </div>

            <div className="p-4 border-t border-gray-200 flex justify-end gap-2">
              <button
                onClick={() => {
                  setShowAnswerModal(false)
                  setSelectedCluster(null)
                  setCanonicalAnswer('')
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-2xl hover:bg-gray-50 transition text-sm"
              >
                Cancel
              </button>
              <button
                onClick={handlePublishAnswer}
                disabled={!canonicalAnswer.trim()}
                className="px-5 py-2 bg-gradient-to-r from-orange-500 to-orange-600 text-white rounded-2xl hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition font-medium text-sm"
              >
                Publish Answer
              </button>
            </div>
            </div>
          </div>
        </div>
      )}

      {/* View Answer Modal */}
      {showViewAnswerModal && selectedCluster && (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4" onClick={() => setShowViewAnswerModal(false)}>
          <div className="bg-white rounded-2xl shadow-2xl max-w-2xl w-full max-h-[85vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="overflow-y-auto max-h-[85vh] p-6">
              {/* Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <CheckCircle className="w-6 h-6 text-green-600" />
                    <span className="text-sm font-medium text-green-700">Answered Cluster</span>
                  </div>
                  <h2 className="text-xl font-bold text-gray-900 mb-2">{selectedCluster.representative_question}</h2>
                  <div className="flex items-center gap-2">
                    <span className="text-xs bg-blue-100 text-blue-700 px-2 py-1 rounded-full">
                      {selectedCluster.count} similar questions
                    </span>
                    {selectedCluster.artifact && (
                      <span className="text-xs bg-purple-50 text-purple-700 px-2 py-1 rounded-full">
                        {selectedCluster.artifact}
                      </span>
                    )}
                    {selectedCluster.section && (
                      <span className="text-xs bg-green-50 text-green-700 px-2 py-1 rounded-full">
                        {selectedCluster.section}
                      </span>
                    )}
                  </div>
                </div>
                <button onClick={() => setShowViewAnswerModal(false)} className="text-gray-400 hover:text-gray-600 transition-colors">
                  <X className="w-5 h-5" />
                </button>
              </div>

              {/* Canonical Answer */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-3 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4 text-green-600" />
                  Canonical Answer
                </h3>
                <div className="bg-green-50 rounded-2xl p-4 border border-green-200">
                  <p className="text-sm text-gray-700 whitespace-pre-wrap">{selectedCluster.canonical_answer}</p>
                </div>
                {selectedCluster.last_updated && (
                  <p className="text-xs text-gray-400 mt-2">Last updated: {selectedCluster.last_updated}</p>
                )}
              </div>

              {/* Similar Questions */}
              <div className="mb-6">
                <h3 className="text-sm font-semibold text-gray-900 mb-3">Similar Questions ({selectedCluster.similar_questions.length})</h3>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {selectedCluster.similar_questions.map((q, i) => (
                    <div key={i} className="bg-gray-50 rounded-xl p-2.5 text-sm text-gray-700 border-l-4 border-blue-300">
                      {q}
                    </div>
                  ))}
                </div>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-3 pt-4 border-t border-gray-200">
                <button 
                  onClick={() => {
                    setShowViewAnswerModal(false)
                    setShowAnswerModal(true)
                    setCanonicalAnswer(selectedCluster.canonical_answer || '')
                  }}
                  className="flex-1 bg-gradient-to-r from-orange-500 to-orange-600 text-white px-4 py-2.5 rounded-2xl font-medium hover:shadow-lg transition-all text-sm flex items-center justify-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  Edit Answer
                </button>
                <button onClick={() => setShowViewAnswerModal(false)} className="px-4 py-2.5 border border-gray-300 rounded-2xl font-medium text-gray-700 hover:bg-gray-50 transition-all text-sm">
                  Close
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
