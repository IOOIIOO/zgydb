"use client";

import { cn } from "@/lib/utils";
import { Check, ChevronRight } from "lucide-react";

interface StepProgressProps {
  currentStep: number;
  completedSteps: boolean[];
  onStepClick?: (step: number) => void;
}

const STEP_LABELS = [
  "性格分析",
  "能力评估",
  "方向选择",
  "深度规划",
  "报告生成",
];

export function StepProgress({
  currentStep,
  completedSteps,
  onStepClick,
}: StepProgressProps) {
  return (
    <nav className="flex items-center justify-center gap-1 py-6" aria-label="步骤进度">
      {STEP_LABELS.map((label, i) => {
        const stepNum = i + 1;
        const isCompleted = completedSteps[i];
        const isCurrent = stepNum === currentStep;
        const isClickable = isCompleted || stepNum === currentStep;

        return (
          <div key={stepNum} className="flex items-center">
            {/* 步骤圆点 */}
            <button
              type="button"
              disabled={!isClickable}
              onClick={() => onStepClick?.(stepNum)}
              className={cn(
                "flex items-center gap-2 px-3 py-1.5 rounded-full text-sm transition-all duration-300",
                isCompleted && "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
                isCurrent && "bg-white/[0.05] text-white border border-white/[0.15]",
                !isCompleted && !isCurrent && "text-white/20 border border-transparent",
                isClickable && "cursor-pointer hover:bg-white/[0.08]",
                !isClickable && "cursor-default",
              )}
            >
              <span
                className={cn(
                  "flex items-center justify-center w-5 h-5 rounded-full text-xs font-semibold",
                  isCompleted && "bg-emerald-500/20 text-emerald-400",
                  isCurrent && "bg-white/10 text-white",
                  !isCompleted && !isCurrent && "bg-transparent text-white/20",
                )}
              >
                {isCompleted ? (
                  <Check className="w-3 h-3" />
                ) : (
                  stepNum
                )}
              </span>
              <span className="hidden sm:inline">{label}</span>
            </button>

            {/* 连线 */}
            {i < STEP_LABELS.length - 1 && (
              <ChevronRight
                className={cn(
                  "w-4 h-4 mx-0.5",
                  isCompleted ? "text-emerald-500/30" : "text-white/10",
                )}
              />
            )}
          </div>
        );
      })}
    </nav>
  );
}
