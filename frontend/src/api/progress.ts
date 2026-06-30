import client from "./client";
import type { UserProgress } from "../types";

/** 获取当前用户流程进度 */
export function getProgress(): Promise<UserProgress> {
  return client.get("/progress");
}
