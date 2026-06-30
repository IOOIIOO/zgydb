import client from "./client";
import type { Direction } from "../types";

/** 获取所有方向列表 */
export function getDirections(): Promise<Direction[]> {
  return client.get("/overview/directions");
}

/** 获取单个方向详情 */
export function getDirectionDetail(id: number): Promise<Direction> {
  return client.get(`/overview/directions/${id}`);
}
