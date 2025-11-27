"use client";

import { TrendingUp, TrendingDown, Minus } from "lucide-react";

interface MasteryBadgeProps {
  topic: string;
  score: number; // 0.0-1.0
  confidence: number; // 0.0-1.0
  size?: "sm" | "md" | "lg";
  showTrend?: boolean;
}

export default function MasteryBadge({
  topic,
  score,
  confidence,
  size = "md",
  showTrend = true,
}: MasteryBadgeProps) {
  // Determine color and status
  const getStatus = (): {
    color: "green" | "yellow" | "red";
    label: string;
    icon: typeof TrendingUp | typeof Minus | typeof TrendingDown;
  } => {
    if (score >= 0.8) return { color: "green", label: "Strong", icon: TrendingUp };
    if (score >= 0.6) return { color: "yellow", label: "Developing", icon: Minus };
    return { color: "red", label: "Needs Practice", icon: TrendingDown };
  };

  const status = getStatus();

  // Size classes
  const sizeClasses = {
    sm: "text-xs px-2 py-1",
    md: "text-sm px-3 py-1.5",
    lg: "text-base px-4 py-2",
  };

  const colorClasses = {
    green: "bg-green-50 text-green-700 border-green-200",
    yellow: "bg-yellow-50 text-yellow-700 border-yellow-200",
    red: "bg-red-50 text-red-700 border-red-200",
  };

  return (
    <div
      className={`inline-flex items-center gap-2 border rounded-full ${colorClasses[status.color]} ${sizeClasses[size]}`}
      title={`Mastery: ${Math.round(score * 100)}% | Confidence: ${Math.round(confidence * 100)}%`}
    >
      {showTrend && <status.icon className="w-4 h-4" />}
      <span className="font-medium">{topic}</span>
      <span className="font-bold">{Math.round(score * 100)}%</span>
    </div>
  );
}
