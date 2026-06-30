/** 行业趋势分析 */
export interface TrendAnalysis {
  id: number;
  direction_id: number;
  position_id: number | null;
  trend_data: {
    overview: string;
    tech_impact: string;
    regional_demand: string;
    salary_trend: string;
    entry_barrier: string;
    personal_analysis: string;
  };
  risk_warnings: string[];
  info_sources: { title: string; url: string }[];
}
