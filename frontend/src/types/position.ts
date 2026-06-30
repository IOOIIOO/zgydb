/** 岗位信息 */
export interface Position {
  id: number;
  title: string;
  description: string;
  direction_id: number;
  education_requirement: string;
  salary_range: string;
}

/** 岗位推荐记录（后端返回的字段平铺） */
export interface RecommendationRecord {
  id: number;
  title: string;
  description: string;
  city: string;
  salary_range: string;
  match_score: number;
  recommendation_reason: string;
}

/** 单维度匹配分析 */
export interface DimensionMatch {
  user_score: number;
  required_score: number;
  verdict: "match" | "partial" | "mismatch";
  detail: string;
}

/** 技能差距 */
export interface SkillGap {
  skill: string;
  importance: string;
  suggestion: string;
}

/** 优势点 */
export interface StrengthPoint {
  skill: string;
  level: string;
}

/** 学历匹配 */
export interface EducationMatch {
  user_education: string;
  required_education: string;
  verdict: string;
}

/** 完整匹配分析 */
export interface MatchAnalysis {
  knowledge_match: DimensionMatch;
  tool_match: DimensionMatch;
  project_match: DimensionMatch;
  overall_match_score: number;
  recommendation_reason: string;
  skill_gaps: SkillGap[];
  strength_points: StrengthPoint[];
  education_match: EducationMatch;
}

/** 岗位详情 + 匹配分析 */
export interface PositionDetail {
  id: number;
  title: string;
  description: string;
  city: string;
  industry: string;
  salary_range: string;
  education_requirement: string;
  match_analysis: MatchAnalysis;
}
