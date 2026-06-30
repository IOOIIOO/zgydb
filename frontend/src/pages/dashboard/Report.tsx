import { useState } from "react";
import { motion } from "framer-motion";
import { generateReport, getReportList, getReportDetail, downloadReportPdf } from "../../api/reports";
import type { Report, ReportDetail } from "../../types";
import { Loader2, FileText, Download, History, RotateCcw } from "lucide-react";

export default function ReportPage() {
  const [report, setReport] = useState<ReportDetail | null>(null);
  const [history, setHistory] = useState<Report[]>([]);
  const [view, setView] = useState<"generate" | "history" | "detail">("generate");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleGenerate = async () => {
    setLoading(true); setError("");
    try { const r = await generateReport(); setReport(r); setView("detail"); }
    catch { setError("生成失败，请确保已完成前四步"); }
    finally { setLoading(false); }
  };

  const loadHistory = async () => {
    setLoading(true);
    try { const h = await getReportList(); setHistory(h); setView("history"); }
    catch { setError("加载失败"); }
    finally { setLoading(false); }
  };

  const viewDetail = async (id: number) => {
    setLoading(true);
    try { const r = await getReportDetail(id); setReport(r); setView("detail"); }
    catch { setError("加载失败"); }
    finally { setLoading(false); }
  };

  const handleDownload = async () => {
    if (!report) return;
    try {
      const blob = await downloadReportPdf(report.id);
      const url = URL.createObjectURL(blob as any);
      const a = document.createElement("a"); a.href = url; a.download = `report_v${report.version}.txt`; a.click();
      URL.revokeObjectURL(url);
    } catch { setError("下载失败"); }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-8">
        <h1 className="text-3xl font-bold"><span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">报告生成</span></h1>
        <p className="text-white/35 mt-2">汇总全部数据，生成你的专属职业规划报告</p>
      </motion.div>

      {error && <div className="mb-6 p-3 rounded-xl bg-rose-500/[0.04] border border-rose-500/[0.1] text-rose-400/80 text-sm">{error}</div>}

      {view === "generate" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center py-16">
          <div className="w-20 h-20 rounded-3xl bg-white/[0.03] border border-white/[0.06] flex items-center justify-center mx-auto mb-6">
            <FileText className="w-9 h-9 text-white/15" />
          </div>
          <h2 className="text-xl text-white/70 font-semibold mb-2">生成综合报告</h2>
          <p className="text-white/25 text-sm mb-8">系统将汇总你前四步的全部数据，生成一份完整的职业规划报告</p>
          <button onClick={handleGenerate} disabled={loading}
            className="px-8 py-3 rounded-xl bg-white text-[#030303] font-semibold hover:bg-white/90 transition-all disabled:opacity-40">
            {loading ? <><Loader2 className="w-4 h-4 inline animate-spin mr-2" />生成中...</> : "生成报告"}
          </button>
          <button onClick={loadHistory} className="block mx-auto mt-4 text-white/20 text-sm hover:text-white/45 transition-colors">
            <History className="w-3.5 h-3.5 inline mr-1" />查看历史报告
          </button>
        </motion.div>
      )}

      {view === "history" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <button onClick={() => setView("generate")} className="text-white/20 hover:text-white/45 text-sm mb-6 transition-colors inline-block">← 返回</button>
          {history.length === 0 ? (
            <div className="p-12 text-center text-white/20 rounded-2xl bg-white/[0.01] border border-white/[0.04]">暂无历史报告</div>
          ) : (
            <div className="space-y-3">
              {history.map((h) => (
                <button key={h.id} onClick={() => viewDetail(h.id)}
                  className="w-full p-5 rounded-2xl bg-white/[0.015] border border-white/[0.06] hover:border-white/[0.15] text-left transition-all">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white/60 font-semibold">版本 {h.version}</h3>
                      <p className="text-white/20 text-xs mt-1">{h.created_at}</p>
                    </div>
                    <Download className="w-4 h-4 text-white/15" />
                  </div>
                </button>
              ))}
            </div>
          )}
        </motion.div>
      )}

      {view === "detail" && report && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          <div className="flex items-center justify-between mb-6">
            <div className="flex gap-4">
              <button onClick={() => setView("generate")} className="text-white/20 hover:text-white/45 text-sm transition-colors">← 返回</button>
              <button onClick={loadHistory} className="text-white/20 hover:text-white/45 text-sm transition-colors">历史</button>
            </div>
            <div className="flex items-center gap-3">
              <span className="text-white/15 text-xs">版本 {report.version}</span>
              <button onClick={handleDownload} className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-white/[0.04] border border-white/[0.08] text-white/35 text-xs hover:bg-white/[0.08] transition-colors">
                <Download className="w-3 h-3" />下载
              </button>
              <button onClick={handleGenerate} className="inline-flex items-center gap-1.5 px-4 py-1.5 rounded-lg bg-white/[0.02] border border-white/[0.06] text-white/25 text-xs hover:bg-white/[0.05] transition-colors">
                <RotateCcw className="w-3 h-3" />重新生成
              </button>
            </div>
          </div>

          {/* 报告内容 — 简洁浅色风格（为PDF做准备） */}
          <div className="rounded-2xl bg-white/[0.02] border border-white/[0.06] p-8 space-y-8 text-sm leading-relaxed">
            <div className="text-center border-b border-white/[0.06] pb-8">
              <h2 className="text-2xl font-bold text-white/80 mb-2">职业规划综合报告</h2>
              <p className="text-white/25">版本 {report.version}</p>
            </div>

            {report.report_data && Object.entries(report.report_data as Record<string, any>).map(([key, val]) => (
              <div key={key}>
                <h3 className="text-white/50 font-semibold mb-2 text-lg">{_sectionTitle(key)}</h3>
                <pre className="text-white/30 whitespace-pre-wrap font-sans text-sm">{JSON.stringify(val, null, 2)}</pre>
              </div>
            ))}
          </div>
        </motion.div>
      )}
    </div>
  );
}

function _sectionTitle(key: string): string {
  return ({ "personality": "性格画像", "ability": "能力画像", "recommendations": "岗位推荐", "trend": "行业趋势", "path": "发展路径" })[key] || key;
}
