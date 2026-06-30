import client from "./client";
import type { Report, ReportDetail } from "../types";

/** 生成综合报告 */
export function generateReport(): Promise<ReportDetail> {
  return client.post("/report/generate");
}

/** 获取历史报告列表 */
export function getReportList(): Promise<Report[]> {
  return client.get("/report/list");
}

/** 获取报告详情 */
export function getReportDetail(reportId: number): Promise<ReportDetail> {
  return client.get(`/report/${reportId}`);
}

/** 下载 PDF 报告 */
export function downloadReportPdf(reportId: number): Promise<Blob> {
  return client.get(`/report/${reportId}/pdf`, {
    responseType: "blob",
  });
}
