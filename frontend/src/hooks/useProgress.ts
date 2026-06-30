import { useState, useEffect } from "react";
import type { UserProgress } from "../types";
import { getProgress } from "../api/progress";

export function useProgress() {
  const [progress, setProgress] = useState<UserProgress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getProgress()
      .then(setProgress)
      .catch(() => {
        // 未登录或网络错误时，显示初始状态
        setProgress({
          current_step: 1,
          step1_completed: false,
          step2_completed: false,
          step3_completed: false,
          step4_completed: false,
          step5_completed: false,
          selected_direction_id: null,
        });
      })
      .finally(() => setLoading(false));
  }, []);

  return { progress, loading };
}
