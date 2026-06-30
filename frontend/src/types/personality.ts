/** MBTI 题目 */
export interface MbtiQuestion {
  id: number;
  dimension: "EI" | "SN" | "TF" | "JP";
  text: string;
  options: {
    a: string;
    b: string;
  };
}

/** 性格测评结果 */
export interface PersonalityResult {
  id: number;
  personality_type: string;
  intensity_level: number;
  ei_score: number;
  sn_score: number;
  tf_score: number;
  jp_score: number;
  strengths: string[];
  weaknesses: string[];
  portrait_description: string;
  direction_tendencies: string[];
}
