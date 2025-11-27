"use client";

import { CheckCircle2, Circle, Flame, Battery, Moon } from "lucide-react";

interface DailyTarget {
  day_number: number;
  date: string;
  focus_topics: string[];
  time_blocks: Array<{
    day: string;
    focus: string;
    duration_hours: number;
  }>;
  gap_check_items: number;
  intensity: string; // "high", "medium", "low", "rest"
}

interface ExamRunwayTimelineProps {
  days: DailyTarget[];
  currentDay?: number;
  examType: string;
}

export default function ExamRunwayTimeline({
  days,
  currentDay = 1,
  examType,
}: ExamRunwayTimelineProps) {
  const getIntensityIcon = (intensity: string) => {
    switch (intensity) {
      case "high":
        return <Flame className="w-4 h-4 text-red-500" />;
      case "medium":
        return <Battery className="w-4 h-4 text-yellow-500" />;
      case "low":
        return <Moon className="w-4 h-4 text-blue-500" />;
      default:
        return <Circle className="w-4 h-4 text-gray-400" />;
    }
  };

  const getIntensityColor = (intensity: string) => {
    switch (intensity) {
      case "high":
        return "border-red-200 bg-red-50";
      case "medium":
        return "border-yellow-200 bg-yellow-50";
      case "low":
        return "border-blue-200 bg-blue-50";
      default:
        return "border-gray-200 bg-gray-50";
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg p-6">
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          7-Day {examType} Exam Prep Runway
        </h2>
        <p className="text-gray-600">Your personalized study plan leading up to the exam</p>
      </div>

      {/* Timeline */}
      <div className="relative">
        {/* Vertical Line */}
        <div className="absolute left-6 top-0 bottom-0 w-0.5 bg-gray-200" />

        {/* Days */}
        <div className="space-y-6">
          {days.map((day, index) => {
            const isCompleted = day.day_number < currentDay;
            const isCurrent = day.day_number === currentDay;
            const totalHours = day.time_blocks.reduce((sum, block) => sum + block.duration_hours, 0);

            return (
              <div key={day.day_number} className="relative flex gap-4">
                {/* Timeline Node */}
                <div className="relative z-10 flex-shrink-0">
                  {isCompleted ? (
                    <div className="w-12 h-12 rounded-full bg-green-500 flex items-center justify-center shadow-md">
                      <CheckCircle2 className="w-6 h-6 text-white" />
                    </div>
                  ) : isCurrent ? (
                    <div className="w-12 h-12 rounded-full bg-blue-500 flex items-center justify-center shadow-lg ring-4 ring-blue-100">
                      <span className="text-white font-bold text-lg">
                        {day.day_number}
                      </span>
                    </div>
                  ) : (
                    <div className="w-12 h-12 rounded-full bg-gray-200 flex items-center justify-center">
                      <span className="text-gray-600 font-medium text-lg">
                        {day.day_number}
                      </span>
                    </div>
                  )}
                </div>

                {/* Day Content */}
                <div className={`flex-1 pb-6 ${isCurrent ? "ring-2 ring-blue-500 ring-offset-2" : ""} ${getIntensityColor(day.intensity)} border-2 rounded-lg p-4 transition-all`}>
                  {/* Day Header */}
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">
                        Day {day.day_number} - {new Date(day.date).toLocaleDateString("en-US", { month: "short", day: "numeric" })}
                      </h3>
                      <div className="flex items-center gap-2 mt-1">
                        {getIntensityIcon(day.intensity)}
                        <span className="text-sm text-gray-600 capitalize">
                          {day.intensity} Intensity
                        </span>
                        <span className="text-sm text-gray-500">• {totalHours}hrs</span>
                      </div>
                    </div>
                    {isCurrent && (
                      <span className="bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full">
                        TODAY
                      </span>
                    )}
                  </div>

                  {/* Focus Topics */}
                  <div className="mb-3">
                    <p className="text-xs font-semibold text-gray-600 uppercase mb-2">
                      Focus Topics:
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {day.focus_topics.map((topic, i) => (
                        <span
                          key={i}
                          className="text-xs bg-white bg-opacity-70 border border-gray-300 text-gray-700 px-2 py-1 rounded-full"
                        >
                          {topic}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Time Blocks */}
                  <div className="space-y-2">
                    {day.time_blocks.map((block, i) => (
                      <div
                        key={i}
                        className="flex items-start gap-2 text-sm bg-white bg-opacity-50 p-2 rounded"
                      >
                        <span className="text-gray-600 font-medium min-w-[100px]">
                          {block.day}:
                        </span>
                        <span className="text-gray-800 flex-1">{block.focus}</span>
                        <span className="text-gray-500 text-xs">
                          {block.duration_hours}hrs
                        </span>
                      </div>
                    ))}
                  </div>

                  {/* Gap Check */}
                  {day.gap_check_items > 0 && (
                    <div className="mt-3 pt-3 border-t border-gray-200">
                      <span className="text-xs font-medium text-purple-700">
                        📊 Evening Gap Check: {day.gap_check_items} questions
                      </span>
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
