import type { PositionDetail } from "../types";

const PREFIX = "pd_cache:";

function key(userId: number, positionId: number): string {
  return `${PREFIX}${userId}:${positionId}`;
}

export function getCachedDetail(userId: number, positionId: number): PositionDetail | null {
  const raw = sessionStorage.getItem(key(userId, positionId));
  if (!raw) return null;
  try {
    return JSON.parse(raw) as PositionDetail;
  } catch {
    return null;
  }
}

export function setCachedDetail(userId: number, positionId: number, detail: PositionDetail): void {
  try {
    sessionStorage.setItem(key(userId, positionId), JSON.stringify(detail));
  } catch {
    // sessionStorage 写入失败（空间不足）静默忽略
  }
}

export function clearUserDetails(userId: number): void {
  const prefix = `${PREFIX}${userId}:`;
  const keysToRemove: string[] = [];
  for (let i = 0; i < sessionStorage.length; i++) {
    const k = sessionStorage.key(i);
    if (k && k.startsWith(prefix)) keysToRemove.push(k);
  }
  keysToRemove.forEach((k) => sessionStorage.removeItem(k));
}
