# 岗位详情面板重排 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将 DirectionSelect 右侧岗位详情面板从单一大卡片拆为三个独立卡片：基本信息、匹配分析、岗位详情

**Architecture:** 纯前端改动，仅重排 DirectionSelect.tsx 的 JSX 结构。不调后端、不解析数据、零性能影响。

**Tech Stack:** React + TypeScript + Tailwind + Framer Motion

## Global Constraints

- 仅修改 `frontend/src/pages/dashboard/DirectionSelect.tsx`
- 不改后端接口和数据结构
- 不增加任何 API 调用或模型推理
- 保持现有动画和过渡效果
- 保持"选定此岗位"按钮功能不变

---

### Task 1: 重排右侧面板为三卡片布局

**Files:**
- Modify: `frontend/src/pages/dashboard/DirectionSelect.tsx:290-490`

**Interfaces:**
- Consumes: `positionDetail` state (PositionDetail type), `loadingDetail` state, `detailError` state, `selectedPositionId` state
- Produces: 相同接口，仅改变 JSX 渲染结构

- [ ] **Step 1: 确认当前文件状态**

读取 `frontend/src/pages/dashboard/DirectionSelect.tsx` 第 290-490 行，确认右侧面板当前结构。

- [ ] **Step 2: 替换右侧面板 JSX**

将加载中/错误/详情三个状态的渲染内容替换为三卡片布局。找到 `{positionDetail ? (` 开始的 JSX 块（约第 323-485 行），替换为：

```tsx
              ) : positionDetail ? (
                <motion.div
                  key={positionDetail.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -12 }}
                  transition={{ duration: 0.25 }}
                  className="space-y-4"
                >
                  {/* ====== 卡片1: 岗位基本信息 ====== */}
                  <div className="p-5 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
                    <div className="flex items-start justify-between mb-3">
                      <h2 className="text-xl font-bold text-white">{positionDetail.title}</h2>
                      <div className="flex-shrink-0 flex flex-col items-center">
                        <span className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-indigo-300 to-rose-300">
                          {positionDetail.match_analysis.overall_match_score}
                        </span>
                        <span className="text-white/20 text-xs">综合匹配度</span>
                      </div>
                    </div>
                    <div className="flex flex-wrap items-center gap-3 text-sm text-white/30">
                      {positionDetail.city && (
                        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.05]">
                          <MapPin className="w-3.5 h-3.5" /> {positionDetail.city}
                        </span>
                      )}
                      {positionDetail.salary_range && (
                        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.05]">
                          <Target className="w-3.5 h-3.5" /> {positionDetail.salary_range}
                        </span>
                      )}
                      {positionDetail.industry && (
                        <span className="inline-flex items-center gap-1 px-3 py-1 rounded-full bg-white/[0.03] border border-white/[0.05]">
                          <Building2 className="w-3.5 h-3.5" /> {positionDetail.industry}
                        </span>
                      )}
                    </div>
                    <div className="mt-3 flex items-center gap-2 text-sm">
                      <Shield className="w-4 h-4 text-emerald-400/60" />
                      <span className="text-white/30">学历要求：</span>
                      <span className="text-white/55 font-medium">{positionDetail.education_requirement || "本科"}</span>
                      <span className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400/80 text-xs">
                        {positionDetail.match_analysis.education_match?.verdict === "match" ? "✓ 满足" : "✗ 不满足"}
                      </span>
                    </div>
                  </div>

                  {/* ====== 卡片2: 匹配分析 ====== */}
                  <div className="p-5 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
                    <h3 className="text-white/50 font-semibold text-sm mb-4 flex items-center gap-2">
                      <Zap className="w-4 h-4 text-amber-400/60" /> 能力维度匹配对比
                    </h3>
                    <div className="space-y-3">
                      {[
                        { key: "knowledge_match", label: "知识", icon: BookOpen, data: positionDetail.match_analysis.knowledge_match },
                        { key: "tool_match", label: "工具", icon: Wrench, data: positionDetail.match_analysis.tool_match },
                        { key: "project_match", label: "项目", icon: TrendingUp, data: positionDetail.match_analysis.project_match },
                      ].map(({ key, label, icon: Icon, data }) => {
                        const matchData = data || { user_score: 0, required_score: 0, verdict: "mismatch", detail: "" };
                        return (
                          <div key={key} className="space-y-1.5">
                            <div className="flex items-center justify-between">
                              <span className="text-white/45 text-sm flex items-center gap-1.5">
                                <Icon className="w-3.5 h-3.5" /> {label}
                              </span>
                              <span className={`text-xs px-2 py-0.5 rounded-full ${
                                matchData.verdict === "match" ? "bg-emerald-500/10 text-emerald-400/80"
                                : matchData.verdict === "partial" ? "bg-amber-500/10 text-amber-400/80"
                                : "bg-rose-500/10 text-rose-400/80"
                              }`}>
                                {matchData.verdict === "match" ? "✓ 匹配" : matchData.verdict === "partial" ? "△ 部分匹配" : "✗ 不匹配"}
                              </span>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-white/20 text-xs w-8 text-right">你 {matchData.user_score}</span>
                              <div className="flex-1 h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                                <div className="h-full rounded-full bg-gradient-to-r from-indigo-400/60 to-indigo-400/30" style={{ width: `${Math.min((matchData.user_score / 100) * 100, 100)}%` }} />
                              </div>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-white/20 text-xs w-8 text-right">要求 {matchData.required_score}</span>
                              <div className="flex-1 h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                                <div className="h-full rounded-full bg-white/[0.15]" style={{ width: `${Math.min((matchData.required_score / 100) * 100, 100)}%` }} />
                              </div>
                            </div>
                            {matchData.detail && <p className="text-white/25 text-xs">{matchData.detail}</p>}
                          </div>
                        );
                      })}
                    </div>

                    {/* 推荐理由 */}
                    {positionDetail.match_analysis.recommendation_reason && (
                      <div className="mt-4 p-4 rounded-xl bg-indigo-500/[0.03] border border-indigo-500/[0.08]">
                        <h3 className="text-indigo-300/60 font-semibold text-sm mb-1.5">💡 匹配分析</h3>
                        <p className="text-white/35 text-sm leading-relaxed">{positionDetail.match_analysis.recommendation_reason}</p>
                      </div>
                    )}
                  </div>

                  {/* ====== 卡片3: 岗位详情 ====== */}
                  {positionDetail.description && (
                    <div className="p-5 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
                      <h3 className="text-white/50 font-semibold text-sm mb-3">📋 岗位详情</h3>
                      <div className="text-white/35 text-sm leading-relaxed whitespace-pre-line max-h-80 overflow-y-auto">
                        {positionDetail.description}
                      </div>
                    </div>
                  )}

                  {/* 优势 + 差距 两列 */}
                  <div className="grid grid-cols-2 gap-4">
                    <div className="p-4 rounded-2xl bg-emerald-500/[0.02] border border-emerald-500/[0.08]">
                      <h3 className="text-emerald-400/60 font-semibold text-sm mb-3 flex items-center gap-1.5">
                        <CheckCircle2 className="w-4 h-4" /> 你的优势
                      </h3>
                      <div className="space-y-2">
                        {(positionDetail.match_analysis.strength_points || []).length > 0 ? (
                          positionDetail.match_analysis.strength_points.map((sp: any) => (
                            <div key={sp.skill} className="flex items-center justify-between">
                              <span className="text-white/55 text-sm">{sp.skill}</span>
                              <span className="text-emerald-400/40 text-xs">{sp.level}</span>
                            </div>
                          ))
                        ) : (
                          <p className="text-white/20 text-sm">暂无优势分析</p>
                        )}
                      </div>
                    </div>
                    <div className="p-4 rounded-2xl bg-amber-500/[0.02] border border-amber-500/[0.08]">
                      <h3 className="text-amber-400/60 font-semibold text-sm mb-3 flex items-center gap-1.5">
                        <AlertCircle className="w-4 h-4" /> 建议提升
                      </h3>
                      <div className="space-y-3">
                        {(positionDetail.match_analysis.skill_gaps || []).length > 0 ? (
                          positionDetail.match_analysis.skill_gaps.map((gap: any) => (
                            <div key={gap.skill}>
                              <div className="flex items-center justify-between mb-0.5">
                                <span className="text-white/55 text-sm">{gap.skill}</span>
                                <span className="text-amber-400/40 text-xs">[{gap.importance}]</span>
                              </div>
                              <p className="text-white/20 text-xs">{gap.suggestion}</p>
                            </div>
                          ))
                        ) : (
                          <p className="text-white/20 text-sm">暂无提升建议</p>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* 底部操作按钮 */}
                  <div className="flex items-center justify-end pt-2 pb-8">
                    <button
                      onClick={handleConfirmPosition}
                      className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white text-[#030303] font-semibold text-sm hover:bg-white/90 transition-all"
                    >
                      选定此岗位，进入深度规划 <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </motion.div>
              ) : null}
```

- [ ] **Step 3: TypeScript 检查**

```bash
cd frontend && npx tsc --noEmit
```
Expected: 零错误

- [ ] **Step 4: 浏览器验证**

打开 `http://localhost:5173`，走完 MBTI → 能力评估 → 方向选择 → 点击岗位，确认右侧面板三个卡片正常显示。

- [ ] **Step 5: Commit**

```bash
git add frontend/src/pages/dashboard/DirectionSelect.tsx
git commit -m "refactor: 岗位详情面板拆分为基本信息/匹配分析/岗位详情三卡片"
```
