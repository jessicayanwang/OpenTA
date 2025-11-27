"use client";

import { useState } from "react";
import { CheckCircle2, XCircle, Clock, Award } from "lucide-react";

interface PopQuizCardProps {
  questionId: string;
  topic: string;
  question: string;
  options: string[];
  onAnswer: (selectedIndex: number, responseTime: number) => void;
  sourceCitation?: string;
}

export default function PopQuizCard({
  questionId,
  topic,
  question,
  options,
  onAnswer,
  sourceCitation,
}: PopQuizCardProps) {
  const [selectedIndex, setSelectedIndex] = useState<number | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [startTime] = useState(Date.now());

  const handleSubmit = async () => {
    if (selectedIndex === null) return;

    const responseTime = (Date.now() - startTime) / 1000;
    setSubmitted(true);

    // Call API
    try {
      const response = await fetch("/api/adaptive/submit-answer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          student_id: "student1", // Get from auth context
          question_id: questionId,
          selected_index: selectedIndex,
          response_time_seconds: responseTime,
        }),
      });

      const data = await response.json();
      setResult(data);
      onAnswer(selectedIndex, responseTime);
    } catch (error) {
      console.error("Error submitting answer:", error);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4 border-l-4 border-blue-500">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Award className="w-5 h-5 text-blue-500" />
          <span className="text-sm font-medium text-blue-700 bg-blue-50 px-3 py-1 rounded-full">
            {topic}
          </span>
        </div>
        <div className="flex items-center gap-1 text-sm text-gray-500">
          <Clock className="w-4 h-4" />
          <span>{Math.floor((Date.now() - startTime) / 1000)}s</span>
        </div>
      </div>

      {/* Question */}
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{question}</h3>

      {/* Options */}
      <div className="space-y-3 mb-4">
        {options.map((option, index) => (
          <button
            key={index}
            onClick={() => !submitted && setSelectedIndex(index)}
            disabled={submitted}
            className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
              selectedIndex === index
                ? "border-blue-500 bg-blue-50"
                : "border-gray-200 hover:border-gray-300 bg-white"
            } ${submitted ? "cursor-not-allowed opacity-75" : "cursor-pointer"} ${
              submitted && result
                ? result.correct && selectedIndex === index
                  ? "border-green-500 bg-green-50"
                  : !result.correct && selectedIndex === index
                  ? "border-red-500 bg-red-50"
                  : ""
                : ""
            }`}
          >
            <div className="flex items-start gap-3">
              <span
                className={`flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                  selectedIndex === index
                    ? "bg-blue-500 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {String.fromCharCode(65 + index)}
              </span>
              <span className="text-gray-800">{option}</span>
            </div>
          </button>
        ))}
      </div>

      {/* Submit Button */}
      {!submitted && (
        <button
          onClick={handleSubmit}
          disabled={selectedIndex === null}
          className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          Submit Answer
        </button>
      )}

      {/* Result */}
      {submitted && result && (
        <div
          className={`mt-4 p-4 rounded-lg ${
            result.correct ? "bg-green-50 border border-green-200" : "bg-red-50 border border-red-200"
          }`}
        >
          <div className="flex items-start gap-3">
            {result.correct ? (
              <CheckCircle2 className="w-6 h-6 text-green-600 flex-shrink-0 mt-0.5" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" />
            )}
            <div className="flex-1">
              <h4 className={`font-semibold ${result.correct ? "text-green-900" : "text-red-900"}`}>
                {result.correct ? "Correct!" : "Not quite"}
              </h4>
              <p className="text-sm text-gray-700 mt-1">{result.explanation}</p>
              {!result.correct && (
                <p className="text-sm text-gray-600 mt-2">
                  <strong>Correct answer:</strong> {result.correct_answer}
                </p>
              )}
              {result.next_review && (
                <p className="text-xs text-gray-500 mt-2">
                  📅 Next review: {new Date(result.next_review).toLocaleDateString()}
                </p>
              )}
            </div>
          </div>

          {/* Mastery Update */}
          {result.mastery_update && (
            <div className="mt-3 pt-3 border-t border-gray-200">
              <div className="flex items-center justify-between text-sm">
                <span className="text-gray-600">Mastery Progress:</span>
                <span className="font-semibold text-blue-700">
                  {Math.round(result.mastery_update.new_mastery * 100)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all"
                  style={{ width: `${result.mastery_update.new_mastery * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>
      )}

      {/* Source Citation */}
      {sourceCitation && (
        <div className="mt-3 text-xs text-gray-500">
          <span className="font-medium">Source:</span> {sourceCitation}
        </div>
      )}
    </div>
  );
}
