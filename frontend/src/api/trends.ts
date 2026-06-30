import client from "./client";
import type { TrendAnalysis } from "../types";

/** 分析选定岗位的行业趋势 */
export function analyzeTrend(directionId: number, positionId: number): Promise<TrendAnalysis> {
  return client.post("/trend/analyze", {
    direction_id: directionId,
    position_id: positionId,
  });
}
