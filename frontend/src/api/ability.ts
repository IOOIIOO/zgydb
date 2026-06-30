import client from "./client";
import type { AbilityPortrait, ResumeSummary } from "../types";

/** 上传简历文件 */
export function uploadResume(file: File): Promise<ResumeSummary> {
  const formData = new FormData();
  formData.append("file", file);
  return client.post("/ability/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
}

/** 提交对话描述文本 */
export function submitDescription(text: string): Promise<ResumeSummary> {
  return client.post("/ability/describe", { text });
}

/** 获取完整能力画像 */
export function getAbilityPortrait(): Promise<AbilityPortrait> {
  return client.get("/ability/portrait");
}

/** 对话响应 */
export interface ChatResponse {
  reply: string;
  next_stage: string;
  portrait_ready: boolean;
}

/** 发送对话消息 */
export function sendChatMessage(
  message: string,
  stage: string
): Promise<ChatResponse> {
  return client.post("/ability/chat", { message, stage });
}
