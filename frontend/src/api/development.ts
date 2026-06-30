import client from "./client";
import type { DevelopmentPath } from "../types";

/** 生成发展路径 */
export function generatePath(directionId: number, positionId: number): Promise<DevelopmentPath> {
  return client.post("/development/generate", {
    direction_id: directionId,
    position_id: positionId,
  });
}

/** 重新生成路径（版本 +1） */
export function regeneratePath(directionId: number, positionId: number): Promise<DevelopmentPath> {
  return client.post("/development/regenerate", {
    direction_id: directionId,
    position_id: positionId,
  });
}
