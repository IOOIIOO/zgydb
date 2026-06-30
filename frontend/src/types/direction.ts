/** 职业发展方向 */
export interface Direction {
  id: number;
  name: string;
  position_examples: string[];
  required_skills: string[];
  development_trend: string;
  sort_order: number;
}
