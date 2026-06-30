import client from "./client";
import type { Direction, RecommendationRecord } from "../types";

/** 获取所有方向列表（方向选择用，与快速了解同源） */
export function getDirectionOptions(): Promise<Direction[]> {
  return client.get("/recommendation/directions");
}

/** 提交选定方向，获取推荐岗位 */
export function getRecommendations(directionId: number): Promise<RecommendationRecord[]> {
  return client.post("/recommendation/recommend", { direction_id: directionId });
}
