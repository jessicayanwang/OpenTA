"use client";

import { AlertCircle, Brain, X } from "lucide-react";
import { useState } from "react";

interface InterventionModalProps {
  isOpen: boolean;
  intervention: {
    type: string;
    reason: string;
    signals: string[];
    suggested_action: string;
  };
  onAccept: () => void;
  onDecline: () => void;
}

export default function InterventionModal({
  isOpen,
  intervention,
  onAccept,
  onDecline,
}: InterventionModalProps) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-2xl max-w-md w-full animate-fade-in">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-600 p-6 rounded-t-xl text-white">
          <div className="flex items-start justify-between">
            <div className="flex items-center gap-3">
              <div className="bg-white bg-opacity-20 p-2 rounded-lg">
                <Brain className="w-6 h-6" />
              </div>
              <div>
                <h3 className="text-lg font-bold">Quick Concept Check</h3>
                <p className="text-sm text-blue-100">Take a 2-minute break to check understanding</p>
              </div>
            </div>
            <button
              onClick={onDecline}
              className="text-white hover:bg-white hover:bg-opacity-20 p-1 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="p-6">
          {/* Reason */}
          <div className="flex items-start gap-3 mb-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="text-sm font-medium text-amber-900">We noticed:</p>
              <p className="text-sm text-amber-800 mt-1">{intervention.reason}</p>
            </div>
          </div>

          {/* Signals Detected */}
          <div className="mb-4">
            <p className="text-xs font-semibold text-gray-600 uppercase mb-2">Detected Patterns:</p>
            <div className="flex flex-wrap gap-2">
              {intervention.signals.map((signal, index) => (
                <span
                  key={index}
                  className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded-full"
                >
                  {signal.replace(/_/g, " ")}
                </span>
              ))}
            </div>
          </div>

          {/* Suggested Action */}
          <div className="mb-6">
            <p className="text-sm text-gray-700">
              <strong>Suggested:</strong> {intervention.suggested_action}
            </p>
          </div>

          {/* Benefits */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
            <p className="text-xs font-semibold text-green-900 mb-2">Why this helps:</p>
            <ul className="text-xs text-green-800 space-y-1">
              <li>✓ Identify any knowledge gaps before they grow</li>
              <li>✓ Get personalized help on weak areas</li>
              <li>✓ Takes just 2 minutes</li>
            </ul>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={onDecline}
              className="flex-1 px-4 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-medium hover:bg-gray-50 transition-colors"
            >
              Maybe Later
            </button>
            <button
              onClick={onAccept}
              className="flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg font-medium hover:from-blue-700 hover:to-purple-700 transition-all shadow-md"
            >
              Start Check
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
