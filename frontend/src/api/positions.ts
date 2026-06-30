import client from "./client";
import type { PositionDetail } from "../types";

/** 获取岗位详情及用户匹配分析 */
export function getPositionDetail(positionId: number): Promise<PositionDetail> {
  return client.get(`/recommendation/positions/${positionId}/detail`);
}
