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
      const a = document.createElement("a"); a.href = url; a.download = `report_v${report.version}.pdf`; a.click();
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

          {/* 报告内容 */}
          <div className="rounded-2xl bg-white/[0.02] border border-white/[0.06] p-8 space-y-8 text-sm leading-relaxed">
            <div className="text-center border-b border-white/[0.06] pb-8">
              <h2 className="text-2xl font-bold text-white/80 mb-2">职业规划综合报告</h2>
              <p className="text-white/25">版本 {report.version}</p>
            </div>

            {report.report_data && (
              <div className="space-y-8">
                {/* 润色文本 */}
                {report.report_data.polished && (
                  <div>
                    <SectionTitle>报告摘要</SectionTitle>
                    <div className="text-white/40 whitespace-pre-wrap leading-relaxed">
                      {report.report_data.polished as string}
                    </div>
                  </div>
                )}

                {/* 性格画像 */}
                {report.report_data.personality && (
                  <div>
                    <SectionTitle>性格画像</SectionTitle>
                    <PersonalitySection data={report.report_data.personality as any} />
                  </div>
                )}

                {/* 能力画像 */}
                {report.report_data.ability && (
                  <div>
                    <SectionTitle>能力画像</SectionTitle>
                    <AbilitySection data={report.report_data.ability as any} />
                  </div>
                )}

                {/* 岗位推荐 */}
                {report.report_data.recommendations && (
                  <div>
                    <SectionTitle>岗位推荐</SectionTitle>
                    <RecommendationsSection data={report.report_data.recommendations as any[]} />
                  </div>
                )}

                {/* 行业趋势 */}
                {report.report_data.trend && (
                  <div>
                    <SectionTitle>行业趋势</SectionTitle>
                    <TrendSection data={report.report_data.trend as any} />
                  </div>
                )}

                {/* 发展路径 */}
                {report.report_data.path && (
                  <div>
                    <SectionTitle>发展路径</SectionTitle>
                    <PathSection data={report.report_data.path as any} />
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      )}
    </div>
  );
}

function SectionTitle({ children }: { children: React.ReactNode }) {
  return <h3 className="text-white/50 font-semibold mb-3 text-lg">{children}</h3>;
}

function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-block px-2.5 py-0.5 rounded-md bg-white/10 border border-white/[0.06] text-white/45 text-xs">{children}</span>;
}

function PersonalitySection({ data }: { data: any }) {
  return (
    <div className="space-y-2 text-white/35 text-sm">
      <p>人格类型：<span className="text-white/65 font-semibold">{data.type}</span>（强度 {data.intensity}）</p>
      <div className="flex gap-4 text-xs text-white/25">
        <span>E-I: {data.ei}</span><span>S-N: {data.sn}</span><span>T-F: {data.tf}</span><span>J-P: {data.jp}</span>
      </div>
      {data.strengths?.length > 0 && <p>优势：{data.strengths.join("、")}</p>}
      {data.weaknesses?.length > 0 && <p>短板：{data.weaknesses.join("、")}</p>}
      {data.portrait && <p className="text-white/20 mt-2">{data.portrait}</p>}
    </div>
  );
}

function AbilitySection({ data }: { data: any }) {
  return (
    <div className="space-y-2 text-white/35 text-sm">
      <p>学历：<span className="text-white/65">{data.education}</span></p>
      <div className="flex gap-6">
        <span>知识评分：<span className="text-white/65">{data.knowledge}</span></span>
        <span>工具评分：<span className="text-white/65">{data.tool}</span></span>
        <span>项目评分：<span className="text-white/65">{data.project}</span></span>
      </div>
      <div className="flex gap-2 flex-wrap">
        <Badge>逻辑: {data.logic}</Badge>
        <Badge>沟通: {data.communication}</Badge>
        <Badge>证书竞赛: {data.cert}</Badge>
        <Badge>学习: {data.learning}</Badge>
      </div>
      {data.strengths?.length > 0 && <p>优势：{data.strengths.join("、")}</p>}
      {data.weaknesses?.length > 0 && <p>短板：{data.weaknesses.join("、")}</p>}
    </div>
  );
}

function RecommendationsSection({ data }: { data: any[] }) {
  return (
    <div className="space-y-2">
      {data.slice(0, 10).map((r: any, i: number) => (
        <div key={i} className="flex items-start gap-3 p-3 rounded-xl bg-white/[0.015] border border-white/[0.05]">
          <span className="text-white/20 text-xs font-mono mt-0.5 shrink-0">{i + 1}.</span>
          <div>
            <span className="text-white/55 text-sm">{r.reason?.slice(0, 150)}</span>
            <span className="text-white/20 text-xs ml-2">匹配度 {r.match_score} 分</span>
          </div>
        </div>
      ))}
    </div>
  );
}

function TrendSection({ data }: { data: any }) {
  const trends = data.trend_data?.trends || [];
  const warnings = data.risk_warnings || [];
  return (
    <div className="space-y-3">
      {trends.map((t: any, i: number) => (
        <div key={i} className="p-3 rounded-xl bg-white/[0.015] border border-white/[0.05]">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-white/60 text-sm font-medium">{t.dimension}</span>
            <span className="text-white/15 text-xs">{t.score}分</span>
          </div>
          <p className="text-white/30 text-xs">{t.content}</p>
        </div>
      ))}
      {warnings.length > 0 && (
        <div className="p-3 rounded-xl bg-amber-500/[0.04] border border-amber-500/[0.1]">
          <p className="text-amber-400/70 text-xs font-medium mb-1">风险提示</p>
          <p className="text-amber-400/40 text-xs">{warnings.join("；")}</p>
        </div>
      )}
    </div>
  );
}

function PathSection({ data }: { data: any }) {
  const stages = [
    { label: "短期", key: "short", data: data.short, color: "border-emerald-500/[0.1] bg-emerald-500/[0.02]" },
    { label: "中期", key: "mid", data: data.mid, color: "border-blue-500/[0.1] bg-blue-500/[0.02]" },
    { label: "长期", key: "long", data: data.long, color: "border-purple-500/[0.1] bg-purple-500/[0.02]" },
  ];
  return (
    <div className="space-y-3">
      {stages.map((s) => {
        const d = s.data;
        if (!d) return null;
        return (
          <div key={s.key} className={`p-4 rounded-xl border ${s.color}`}>
            <h4 className="text-white/55 text-sm font-semibold mb-2">{s.label}（{d.duration}）</h4>
            <p className="text-white/35 text-sm mb-1">{d.goal}</p>
            {d.skills?.length > 0 && <p className="text-white/20 text-xs">技能：{d.skills.join("、")}</p>}
            {d.milestones?.length > 0 && <p className="text-white/20 text-xs">里程碑：{d.milestones.join("、")}</p>}
            {d.directions?.length > 0 && <p className="text-white/20 text-xs">方向：{d.directions.join("、")}</p>}
            {d.advanced_skills?.length > 0 && <p className="text-white/20 text-xs">高阶技能：{d.advanced_skills.join("、")}</p>}
          </div>
        );
      })}
    </div>
  );
}
