/** 综合报告 */
export interface Report {
  id: number;
  user_id: number;
  version: number;
  created_at: string;
  has_pdf: boolean;
}

/** 报告详情 */
export interface ReportDetail extends Report {
  report_data: Record<string, unknown>;
  pdf_path: string | null;
}
