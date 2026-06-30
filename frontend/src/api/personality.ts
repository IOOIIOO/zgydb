import client from "./client";
import type { MbtiQuestion, PersonalityResult } from "../types";

/** 获取 MBTI 题目列表 */
export function getMbtiQuestions(): Promise<MbtiQuestion[]> {
  return client.get("/personality/questions");
}

/** 提交答案，返回性格结果 */
export function submitMbtiAnswers(answers: Record<number, string>): Promise<PersonalityResult> {
  return client.post("/personality/submit", { answers });
}

/** 获取已保存的性格结果 */
export function getPersonalityResult(): Promise<PersonalityResult> {
  return client.get("/personality/result");
}
