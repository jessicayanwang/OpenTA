'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { BarChart3, Users, Search, MessageSquare, User } from 'lucide-react'
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
  
  // Clusters
  const [clusters, setClusters] = useState<QuestionCluster[]>([])
  const [selectedCluster, setSelectedCluster] = useState<QuestionCluster | null>(null)
  const [canonicalAnswer, setCanonicalAnswer] = useState('')
  const [showAnswerModal, setShowAnswerModal] = useState(false)
  
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
        setContentGaps(data.gaps)
      } else if (activeTab === 'clusters') {
        const res = await fetch('http://localhost:8000/api/professor/clusters?course_id=cs50&semantic=true&min_count=2')
        const data = await res.json()
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

  const handlePublishAnswer = async () => {
    if (!selectedCluster || !canonicalAnswer.trim()) return

    try {
      await fetch('http://localhost:8000/api/professor/canonical-answer', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          cluster_id: selectedCluster.cluster_id,
          answer_text: canonicalAnswer,
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
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="p-4 border-b border-gray-200">
          <Logo size="sm" showText={true} />
          <div className="text-xs text-gray-500 mt-3">Professor Console</div>
        </div>
        
        {/* Navigation - Increased Spacing */}
        <nav className="px-4 py-4 space-y-1">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`w-full px-4 py-3 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30 ${
              activeTab === 'dashboard' 
                ? 'text-gray-900 font-semibold' 
                : 'text-gray-600 hover:text-gray-900 hover:font-semibold'
            }`}
          >
            <div className={`absolute left-0 w-1 rounded-r transition-all duration-200 ${
              activeTab === 'dashboard' ? 'h-full bg-orange-500' : 'h-0 bg-orange-500 group-hover:h-full'
            }`}></div>
            <BarChart3 size={18} className={`transition-colors ${
              activeTab === 'dashboard' ? 'text-orange-500' : 'text-gray-500 group-hover:text-orange-500'
            }`} />
            <span>Dashboard</span>
          </button>
          <button
            onClick={() => setActiveTab('students')}
            className={`w-full px-4 py-3 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30 ${
              activeTab === 'students' 
                ? 'text-gray-900 font-semibold' 
                : 'text-gray-600 hover:text-gray-900 hover:font-semibold'
            }`}
          >
            <div className={`absolute left-0 w-1 rounded-r transition-all duration-200 ${
              activeTab === 'students' ? 'h-full bg-orange-500' : 'h-0 bg-orange-500 group-hover:h-full'
            }`}></div>
            <Users size={18} className={`transition-colors ${
              activeTab === 'students' ? 'text-orange-500' : 'text-gray-500 group-hover:text-orange-500'
            }`} />
            <span>Student Analytics</span>
          </button>
          <button
            onClick={() => setActiveTab('content-gaps')}
            className={`w-full px-4 py-3 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30 ${
              activeTab === 'content-gaps' 
                ? 'text-gray-900 font-semibold' 
                : 'text-gray-600 hover:text-gray-900 hover:font-semibold'
            }`}
          >
            <div className={`absolute left-0 w-1 rounded-r transition-all duration-200 ${
              activeTab === 'content-gaps' ? 'h-full bg-orange-500' : 'h-0 bg-orange-500 group-hover:h-full'
            }`}></div>
            <Search size={18} className={`transition-colors ${
              activeTab === 'content-gaps' ? 'text-orange-500' : 'text-gray-500 group-hover:text-orange-500'
            }`} />
            <span>Content Gaps</span>
          </button>
          <button
            onClick={() => setActiveTab('clusters')}
            className={`w-full px-4 py-3 text-left text-sm rounded-lg transition-all duration-200 flex items-center gap-3 group relative focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30 ${
              activeTab === 'clusters' 
                ? 'text-gray-900 font-semibold' 
                : 'text-gray-600 hover:text-gray-900 hover:font-semibold'
            }`}
          >
            <div className={`absolute left-0 w-1 rounded-r transition-all duration-200 ${
              activeTab === 'clusters' ? 'h-full bg-orange-500' : 'h-0 bg-orange-500 group-hover:h-full'
            }`}></div>
            <MessageSquare size={18} className={`transition-colors ${
              activeTab === 'clusters' ? 'text-orange-500' : 'text-gray-500 group-hover:text-orange-500'
            }`} />
            <span>Question Clusters</span>
          </button>
        </nav>

        {/* Spacer */}
        <div className="flex-1"></div>

        {/* Bottom */}
        <div className="px-4 py-4 border-t border-gray-200">
          <button
            onClick={() => router.push('/login')}
            className="w-full px-4 py-2.5 text-left text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 rounded-lg transition-all duration-200 flex items-center gap-3 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-opacity-30"
          >
            <User size={18} className="text-gray-500" />
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
                  <h1 className="text-3xl font-normal text-gray-900 mb-2">Dashboard Overview</h1>
                  <p className="text-gray-600 mb-8">Course health metrics for the last 7 days</p>

                  {/* Metrics Cards */}
                  <div className="grid grid-cols-4 gap-4 mb-8">
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <div className="text-sm text-gray-600 mb-1">Total Questions</div>
                      <div className="text-3xl font-semibold text-gray-900">{metrics.total_questions}</div>
                    </div>
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <div className="text-sm text-gray-600 mb-1">Avg Confidence</div>
                      <div className={`text-3xl font-semibold ${getConfidenceColor(metrics.avg_confidence)}`}>
                        {(metrics.avg_confidence * 100).toFixed(0)}%
                      </div>
                    </div>
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <div className="text-sm text-gray-600 mb-1">Struggling Students</div>
                      <div className="text-3xl font-semibold text-red-600">{metrics.struggling_students}</div>
                    </div>
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <div className="text-sm text-gray-600 mb-1">Unresolved Items</div>
                      <div className="text-3xl font-semibold text-yellow-600">{metrics.unresolved_items}</div>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    {/* Top Confusion Topics */}
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">🔥 Top Confusion Topics</h2>
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
                    <div className="bg-white rounded-xl border border-gray-200 p-6">
                      <h2 className="text-lg font-semibold text-gray-900 mb-4">📝 Recent Activity</h2>
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
                  <h1 className="text-3xl font-normal text-gray-900 mb-2">Student Analytics</h1>
                  <p className="text-gray-600 mb-8">Individual student engagement and performance</p>

                  {students.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">No student data available</div>
                  ) : (
                    <div className="grid grid-cols-1 gap-4">
                      {students.map((student) => (
                        <div key={student.student_id} className="bg-white rounded-xl border border-gray-200 p-6">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center gap-3 mb-2">
                                <h3 className="text-lg font-semibold text-gray-900">{student.student_id}</h3>
                                <span className={`text-xs px-2 py-1 rounded-full font-medium ${getStatusColor(student.status)}`}>
                                  {student.status}
                                </span>
                              </div>
                              <div className="grid grid-cols-4 gap-4 text-sm">
                                <div>
                                  <div className="text-gray-500">Questions</div>
                                  <div className="font-semibold text-gray-900">{student.questions_asked}</div>
                                </div>
                                <div>
                                  <div className="text-gray-500">Avg Confidence</div>
                                  <div className={`font-semibold ${getConfidenceColor(student.avg_confidence)}`}>
                                    {(student.avg_confidence * 100).toFixed(0)}%
                                  </div>
                                </div>
                                <div>
                                  <div className="text-gray-500">Confusion Signals</div>
                                  <div className="font-semibold text-red-600">{student.confusion_signals}</div>
                                </div>
                                <div>
                                  <div className="text-gray-500">Last Active</div>
                                  <div className="font-semibold text-gray-900">
                                    {student.last_active ? new Date(student.last_active).toLocaleDateString() : 'Never'}
                                  </div>
                                </div>
                              </div>
                              <div className="mt-3">
                                <div className="text-xs text-gray-500 mb-1">Topics Explored:</div>
                                <div className="flex flex-wrap gap-1">
                                  {student.topics.map((topic, i) => (
                                    <span key={i} className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                                      {topic}
                                    </span>
                                  ))}
                                </div>
                              </div>
                            </div>
                            {student.status === 'struggling' && (
                              <button className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 text-sm font-medium">
                                Intervene
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Content Gaps Tab */}
              {activeTab === 'content-gaps' && (
                <div>
                  <h1 className="text-3xl font-normal text-gray-900 mb-2">Content Gap Analysis</h1>
                  <p className="text-gray-600 mb-8">Topics with low-confidence responses that may need more materials</p>

                  {contentGaps.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">No content gaps identified</div>
                  ) : (
                    <div className="space-y-4">
                      {contentGaps.map((gap, i) => (
                        <div key={i} className={`rounded-xl border p-6 ${
                          gap.priority === 'high' ? 'bg-red-50 border-red-200' : 'bg-yellow-50 border-yellow-200'
                        }`}>
                          <div className="flex items-start justify-between mb-3">
                            <div>
                              <h3 className="text-lg font-semibold text-gray-900">{gap.topic}</h3>
                              <p className="text-sm text-gray-600 mt-1">{gap.question_count} low-confidence questions</p>
                            </div>
                            <span className={`text-xs px-2 py-1 rounded-full font-medium ${
                              gap.priority === 'high' ? 'bg-red-200 text-red-900' : 'bg-yellow-200 text-yellow-900'
                            }`}>
                              {gap.priority} priority
                            </span>
                          </div>
                          <div className="mb-3">
                            <div className="text-sm font-medium text-gray-700 mb-2">Example Questions:</div>
                            <ul className="space-y-1">
                              {gap.example_questions.map((q, j) => (
                                <li key={j} className="text-sm text-gray-600">• {q}</li>
                              ))}
                            </ul>
                          </div>
                          <div className="bg-white border border-gray-200 rounded-lg p-3">
                            <div className="text-xs font-medium text-gray-700 mb-1">💡 Suggested Action:</div>
                            <div className="text-sm text-gray-900">{gap.suggested_action}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Clusters Tab */}
              {activeTab === 'clusters' && (
                <div>
                  <h1 className="text-3xl font-normal text-gray-900 mb-2">Question Clusters</h1>
                  <p className="text-gray-600 mb-8">AI-powered semantic grouping of similar questions</p>

                  {clusters.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">
                      <p>No question clusters yet</p>
                      <p className="text-sm mt-2">Students need to ask questions first</p>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {clusters.map((cluster) => (
                        <div key={cluster.cluster_id} className="bg-white rounded-xl border border-gray-200 p-6">
                          <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                              <div className="flex items-center gap-2 mb-3">
                                <span className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full font-medium">
                                  {cluster.count} similar questions
                                </span>
                                {cluster.artifact && (
                                  <span className="bg-purple-50 text-purple-700 text-xs px-2 py-1 rounded-full">
                                    {cluster.artifact}
                                  </span>
                                )}
                                {cluster.section && (
                                  <span className="bg-green-50 text-green-700 text-xs px-2 py-1 rounded-full">
                                    {cluster.section}
                                  </span>
                                )}
                                {cluster.canonical_answer_id && (
                                  <span className="bg-green-100 text-green-800 text-xs px-2 py-1 rounded-full">
                                    ✓ Has canonical answer
                                  </span>
                                )}
                              </div>
                              <p className="text-lg text-gray-900 mb-3 font-medium">
                                {cluster.representative_question}
                              </p>
                              <details className="text-sm">
                                <summary className="cursor-pointer text-gray-600 hover:text-gray-900 font-medium">
                                  View all {cluster.similar_questions.length} questions
                                </summary>
                                <ul className="mt-3 ml-4 space-y-2">
                                  {cluster.similar_questions.slice(0, 10).map((q, i) => (
                                    <li key={i} className="text-gray-600">• {q}</li>
                                  ))}
                                  {cluster.similar_questions.length > 10 && (
                                    <li className="text-gray-500 italic">+ {cluster.similar_questions.length - 10} more...</li>
                                  )}
                                </ul>
                              </details>
                            </div>
                            {!cluster.canonical_answer_id && (
                              <button
                                onClick={() => handleCreateAnswer(cluster)}
                                className="px-4 py-2 bg-gradient-to-br from-orange-400 to-orange-600 text-white rounded-lg hover:from-orange-500 hover:to-orange-700 text-sm font-medium transition"
                              >
                                Create Answer
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </>
          )}
        </div>
      </div>

      {/* Canonical Answer Modal */}
      {showAnswerModal && selectedCluster && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-2xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-2xl font-semibold text-gray-900">Create Canonical Answer</h2>
              <p className="text-sm text-gray-600 mt-1">
                This answer will automatically respond to similar questions
              </p>
            </div>
            
            <div className="p-6">
              <div className="mb-4">
                <div className="text-sm font-medium text-gray-700 mb-2">Representative Question:</div>
                <div className="bg-gray-50 p-3 rounded-lg text-gray-900">
                  {selectedCluster.representative_question}
                </div>
              </div>

              <div className="mb-4">
                <div className="text-sm font-medium text-gray-700 mb-2">
                  Will answer {selectedCluster.count} similar questions
                </div>
              </div>

              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Canonical Answer (Markdown supported)
                </label>
                <textarea
                  value={canonicalAnswer}
                  onChange={(e) => setCanonicalAnswer(e.target.value)}
                  className="w-full h-64 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 font-mono text-sm"
                  placeholder="Write a comprehensive answer that will help all students asking similar questions...

You can use markdown:
- **bold** for emphasis
- `code` for code snippets
- Lists and formatting"
                />
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
                <div className="text-xs font-medium text-blue-900 mb-1">💡 Tip:</div>
                <div className="text-xs text-blue-800">
                  Write a clear, comprehensive answer that addresses the core question. This will be shown to all students asking similar questions in the future.
                </div>
              </div>
            </div>

            <div className="p-6 border-t border-gray-200 flex justify-end gap-3">
              <button
                onClick={() => {
                  setShowAnswerModal(false)
                  setSelectedCluster(null)
                  setCanonicalAnswer('')
                }}
                className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handlePublishAnswer}
                disabled={!canonicalAnswer.trim()}
                className="px-6 py-2 bg-gradient-to-br from-orange-400 to-orange-600 text-white rounded-lg hover:from-orange-500 hover:to-orange-700 disabled:opacity-50 disabled:cursor-not-allowed transition font-medium"
              >
                Publish Answer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
