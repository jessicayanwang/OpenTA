"use client";

import { useState, useEffect } from "react";
import PopQuizCard from "@/components/adaptive/PopQuizCard";
import InterventionModal from "@/components/adaptive/InterventionModal";
import MasteryBadge from "@/components/adaptive/MasteryBadge";
import RefresherChip from "@/components/adaptive/RefresherChip";
import ExamRunwayTimeline from "@/components/adaptive/ExamRunwayTimeline";
import NotificationBell from "@/components/adaptive/NotificationBell";

export default function AdaptiveLearningDemo() {
  const [quizItems, setQuizItems] = useState<any[]>([]);
  const [masteryData, setMasteryData] = useState<any>(null);
  const [showIntervention, setShowIntervention] = useState(false);
  const [examRunway, setExamRunway] = useState<any>(null);
  const [activeTab, setActiveTab] = useState("daily-quiz");

  useEffect(() => {
    // Load daily quiz
    fetchDailyQuiz();
    // Load mastery status
    fetchMasteryStatus();
  }, []);

  const fetchDailyQuiz = async () => {
    try {
      const response = await fetch("/api/adaptive/daily-quiz?student_id=student1&count=3");
      const data = await response.json();
      setQuizItems(data.items || []);
    } catch (error) {
      console.error("Error fetching quiz:", error);
    }
  };

  const fetchMasteryStatus = async () => {
    try {
      const response = await fetch("/api/adaptive/mastery-status?student_id=student1");
      const data = await response.json();
      setMasteryData(data);
    } catch (error) {
      console.error("Error fetching mastery:", error);
    }
  };

  const loadExamRunway = async () => {
    try {
      const examDate = new Date();
      examDate.setDate(examDate.getDate() + 7);
      
      const response = await fetch("/api/adaptive/exam-runway", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: "student1",
          exam_date: examDate.toISOString(),
          exam_type: "midterm",
          hours_per_day: 3.0,
        }),
      });
      const data = await response.json();
      setExamRunway(data);
    } catch (error) {
      console.error("Error loading exam runway:", error);
    }
  };

  const handleQuizAnswer = (index: number, responseTime: number) => {
    console.log("Answer submitted:", index, responseTime);
    // Refresh mastery after answer
    setTimeout(fetchMasteryStatus, 1000);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Adaptive Learning Demo</h1>
              <p className="text-sm text-gray-600">
                Test all adaptive learning features
              </p>
            </div>
            <NotificationBell />
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="bg-white rounded-lg shadow mb-6">
          <div className="border-b border-gray-200">
            <nav className="flex -mb-px">
              {[
                { id: "daily-quiz", label: "Daily Quiz" },
                { id: "mastery", label: "Mastery Status" },
                { id: "exam-runway", label: "Exam Runway" },
                { id: "interventions", label: "Interventions" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-6 py-3 text-sm font-medium border-b-2 transition-colors ${
                    activeTab === tab.id
                      ? "border-blue-500 text-blue-600"
                      : "border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300"
                  }`}
                >
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === "daily-quiz" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                ☀️ Your Daily Practice (3 items)
              </h2>
              <p className="text-gray-600 mb-6">
                Personalized questions based on spaced repetition and your weak topics
              </p>
              
              {quizItems.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-500">Loading quiz items...</p>
                </div>
              ) : (
                quizItems.map((item, index) => (
                  <PopQuizCard
                    key={item.question_id}
                    questionId={item.question_id}
                    topic={item.topic}
                    question={item.question}
                    options={item.options}
                    onAnswer={handleQuizAnswer}
                    sourceCitation={item.source_citation}
                  />
                ))
              )}
            </div>
          </div>
        )}

        {activeTab === "mastery" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                📊 Mastery Status
              </h2>
              
              {masteryData ? (
                <>
                  {/* Overall Progress */}
                  <div className="mb-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg">
                    <p className="text-sm text-gray-600 mb-2">Overall Progress</p>
                    <div className="flex items-center gap-4">
                      <div className="flex-1">
                        <div className="w-full bg-gray-200 rounded-full h-4">
                          <div
                            className="bg-gradient-to-r from-blue-600 to-purple-600 h-4 rounded-full transition-all"
                            style={{ width: `${masteryData.overall_progress * 100}%` }}
                          />
                        </div>
                      </div>
                      <span className="text-2xl font-bold text-gray-900">
                        {Math.round(masteryData.overall_progress * 100)}%
                      </span>
                    </div>
                  </div>

                  {/* Topics */}
                  <div className="space-y-4">
                    <h3 className="font-semibold text-gray-900">Topics Mastery</h3>
                    {masteryData.topics.length === 0 ? (
                      <p className="text-gray-500">
                        No data yet. Complete some quiz items to see your progress!
                      </p>
                    ) : (
                      <div className="space-y-3">
                        {masteryData.topics.map((topic: any, index: number) => (
                          <div
                            key={index}
                            className="flex items-center justify-between p-4 bg-gray-50 rounded-lg"
                          >
                            <div className="flex-1">
                              <MasteryBadge
                                topic={topic.topic}
                                score={topic.mastery_score}
                                confidence={topic.confidence}
                              />
                              <p className="text-xs text-gray-500 mt-2">
                                {topic.correct}/{topic.attempts} correct • Streak: {topic.streak}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Weak Topics */}
                  {masteryData.weak_topics.length > 0 && (
                    <div className="mt-6">
                      <h3 className="font-semibold text-gray-900 mb-3">
                        Needs Practice
                      </h3>
                      <div className="space-y-2">
                        {masteryData.weak_topics.map((topic: string, index: number) => (
                          <RefresherChip
                            key={index}
                            topic={topic}
                            reason="Below 60% mastery - extra practice recommended"
                            scheduled="Next quiz session"
                          />
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-gray-500">Loading mastery data...</p>
              )}
            </div>
          </div>
        )}

        {activeTab === "exam-runway" && (
          <div className="space-y-6">
            {!examRunway ? (
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <h2 className="text-xl font-bold text-gray-900 mb-4">
                  🎯 7-Day Exam Prep Runway
                </h2>
                <p className="text-gray-600 mb-6">
                  Generate a personalized 7-day study plan for your upcoming exam
                </p>
                <button
                  onClick={loadExamRunway}
                  className="bg-gradient-to-r from-blue-600 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all"
                >
                  Generate Exam Runway
                </button>
              </div>
            ) : (
              <ExamRunwayTimeline
                days={examRunway.daily_targets}
                currentDay={1}
                examType={examRunway.exam_type}
              />
            )}
          </div>
        )}

        {activeTab === "interventions" && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">
                💡 Smart Interventions
              </h2>
              <p className="text-gray-600 mb-6">
                The system detects when you're struggling and offers help
              </p>

              <div className="space-y-4">
                <div className="border-2 border-gray-200 rounded-lg p-4">
                  <h3 className="font-semibold text-gray-900 mb-2">
                    Triggers for Intervention:
                  </h3>
                  <ul className="space-y-2 text-sm text-gray-700">
                    <li>✓ 3+ hint requests</li>
                    <li>✓ 10+ minutes without progress</li>
                    <li>✓ Repeated errors (same type)</li>
                    <li>✓ Excessive copy/paste (5+ times)</li>
                    <li>✓ Low confidence language ("I don't know", "confused")</li>
                    <li>✓ 5+ rapid questions in 5 minutes</li>
                  </ul>
                </div>

                <button
                  onClick={() => setShowIntervention(true)}
                  className="w-full bg-amber-500 text-white py-3 rounded-lg font-medium hover:bg-amber-600 transition-colors"
                >
                  Preview Intervention Modal
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Intervention Modal */}
      <InterventionModal
        isOpen={showIntervention}
        intervention={{
          type: "concept_check",
          reason: "You've requested several hints and been working on this for a while",
          signals: ["multiple_hints", "long_dwell"],
          suggested_action: "Take a quick 2-question concept check to identify gaps",
        }}
        onAccept={() => {
          setShowIntervention(false);
          alert("Concept check would start here!");
        }}
        onDecline={() => {
          setShowIntervention(false);
        }}
      />
    </div>
  );
}
