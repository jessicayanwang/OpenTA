"use client";

import { RefreshCw, Clock } from "lucide-react";

interface RefresherChipProps {
  topic: string;
  reason: string;
  scheduled: string; // e.g., "Tonight", "Tomorrow", "This evening"
  onView?: () => void;
}

export default function RefresherChip({ topic, reason, scheduled, onView }: RefresherChipProps) {
  return (
    <div className="flex items-start gap-3 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 border-l-4 border-blue-500 rounded-lg shadow-sm">
      {/* Icon */}
      <div className="bg-blue-500 p-2 rounded-lg flex-shrink-0">
        <RefreshCw className="w-5 h-5 text-white" />
      </div>

      {/* Content */}
      <div className="flex-1">
        <div className="flex items-center gap-2 mb-1">
          <span className="text-sm font-bold text-blue-900">Refresher Added</span>
          <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full">{topic}</span>
        </div>
        <p className="text-xs text-gray-600 mb-2">{reason}</p>
        <div className="flex items-center gap-1 text-xs text-gray-500">
          <Clock className="w-3 h-3" />
          <span>Scheduled: {scheduled}</span>
        </div>
      </div>

      {/* Action */}
      {onView && (
        <button
          onClick={onView}
          className="text-xs text-blue-600 hover:text-blue-700 font-medium hover:underline"
        >
          View
        </button>
      )}
    </div>
  );
}
