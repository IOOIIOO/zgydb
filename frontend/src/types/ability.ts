/** 能力画像 */
export interface AbilityPortrait {
  id: number;
  education: string;
  knowledge_score: number;
  tool_score: number;
  project_score: number;
  scoring_basis: Record<string, string>;
  logic_label: string;
  communication_label: string;
  cert_competition_label: string;
  learning_label: string;
  label_inference_basis: Record<string, string>;
  strengths: string[];
  weaknesses: string[];
}

/** 证书记录 */
export interface CertificateRecord {
  id: number;
  certificate_name: string;
  level: number;
  level_name: string;
  score: number;
}

/** 竞赛记录 */
export interface CompetitionRecord {
  id: number;
  competition_name: string;
  level: number;
  level_name: string;
  bonus_score: number;
}

/** 简历提取信息摘要 */
export interface ResumeSummary {
  education: string;
  skills: string[];
  certificates: { name: string; level: string }[];
  competitions: { name: string; level: string }[];
  projects: string[];
  raw_text: string;
}
