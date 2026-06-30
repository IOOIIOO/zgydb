/** 发展路径 */
export interface DevelopmentPath {
  id: number;
  direction_id: number;
  position_id: number | null;
  short_term_path: {
    duration: string;
    skills: string[];
    resources: { name: string; url: string; type: string }[];
  };
  mid_term_path: {
    duration: string;
    skills: string[];
    milestones: string[];
  };
  long_term_path: {
    duration: string;
    directions: string[];
    advanced_skills: string[];
  };
  resource_list: { name: string; url: string; type: string; isbn?: string }[];
  version: number;
}
