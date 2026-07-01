# 进度日志

## 会话：2026-07-01 全链本地化（第16轮）
- **状态：** complete
- 触发：使用体验反馈 — AI 慢、上传慢、对话无结束标志、方向页卡住、布局混乱
- P1: 创建 `unified_analyzer.py` — 6 个本地 LLM 函数替代百炼
- P2: 重写 `ability_service.py` — 移除 ThreadPoolExecutor，单次本地调用
- P3: 本地化 `analyze_position_match` / `polish_report` / 发展路径生成
- P4: 修复对话收集 — 前端 ref 累积全部消息，portrait_ready 时拼起来调 describe
- P5: 前端优化 — 删 800ms 延迟、上传进度、生成雷达图按钮、loading 反馈
- P6: 岗位详情三卡片布局 — 基本信息 / 匹配分析 / 岗位详情
- P7: 模型对比 — Qwen2.5-7B (14s) vs DeepSeek R1 (54s)，选 Qwen
- 验证：全流程 5/5 PASS，纯本地 24.8s
- 新建：`unified_analyzer.py`, `陀螺报告.md`
- 修改：ability_service, model_interface, development_service, report_service, ability router, recommendation router, Ability.tsx, DirectionSelect.tsx, vite.config.ts

---

## 会话：2026-07-01 第五轮问题修复（第15轮）
- **状态：** complete
- 触发：第五轮使用体验报告 + 旧项目(纯大模型)经验借鉴
- F1: analyze_position_match 不再独立打 overall_match_score（LLM只做定性分析）
- F2: 详情接口 overall_match_score 直接从 embedding 取（列表/详情分数一致）
- F3: 批量推荐理由 batch_write_recommendations（1次LLM替代10次并行）+ (title,city)去重
- F4: 发展路径 LLM prompt 传入完整用户画像（学历/技能/分数/优劣势）
- F5: search_trends/search_resources prompt 强化 URL 真实性约束
- F6: 前端 Report.tsx 结构化渲染（PersonalitySection/AbilitySection/RecommendationsSection/TrendSection/PathSection）
- F7: 后端 PDF _generate_pdf 改用人类可读格式化函数替代 json.dumps
- 验证：Backend 4 modules OK, Frontend TypeScript OK
- 6 files, targeted changes

---

## 会话：2026-07-01 深度检修（第14轮）
- **状态：** complete
- 触发：20260701使用体验报告，第13轮修复后仍存问题
- P0: ability_service cert_competition_label 从 M4 独立计算
- P1-6: 保持 embedding 原始分数不拉伸
- P1-7: 详情接口同时返回 embedding_score
- P1: ThreadPoolExecutor 并行化 (~18s×10 → ~30s)
- P1: 4个 router 流程顺序约束校验
- P2: reportlab 安装、docstring 更新、embedding 优化、发展路径 LLM 个性化
- 验证：App 14 routes OK, MBTI OK, cert_competition logic OK
- 24 files, +294/-655

---

## 会话：2026-06-30 代码检修（第13轮）
- **状态：** complete
- 触发：Codex 使用体验报告 + 稳定性对比报告
- 删除：fake_data/ 全部6个文件，MODEL_MODE 开关
- 修复：P0×4 + P1×3 + P2×2 = 9个问题
- Code Review：Critical 1个已修复，Important 4个已修复
- 验证：App 14 routes OK，MBTI E=10 S=10 T=10 J=10，example.com 零残留

---

## 会话：2026-06-30 百炼 qwen3.7-plus 全面接入（第8.7轮）
- **状态：** complete
- 创建：BailianClient(共享客户端) + bailian_llm.py(8函数)
- 重写：model_interface.py 为统一 MODEL_MODE=real 开关
- 验证：全部 8 函数 PASS，联网搜索正常
- 11/11 AI 任务已覆盖真实模型（仅 M1 多模态待接）

## 会话：2026-06-30 能力评估对话式重构（第8.6轮）
- **状态：** complete
- 触发：能力评估应有对话窗口，上传简历作为对话框功能
- 交互模式：AI引导分阶段提问（教育→技能→项目→证书→画像）
- 布局：上下分屏（可折叠雷达图+聊天区域）
- 后端：FAKE_chat_response + POST /ability/chat
- 前端：ChatMessages + ChatInput 组件，Ability.tsx全面重写
- 验证：6阶段全流程PASS，TypeScript零错误

## 会话：2026-06-30 岗位选择交互重设计

### 第8.5轮：岗位选择双栏重设计
- **状态：** complete
- 触发：验收时发现深度规划应基于岗位而非方向
- 后端：新增 `FAKE_analyze_position_match` + `GET /recommendation/positions/{id}/detail`
- 前端：DirectionSelect 改为双栏(35/65)布局，右侧展示匹配分析
- Planning 改为从 localStorage 读取 selected_position_id
- trend/development API 的 position_id 改为必传
- 验证：新接口200，全流程9步PASS

## 会话：2026-06-29

### 第1-3.5轮
- **状态：** complete
- 创建/修改的文件：项目骨架全部文件、12模型、seed脚本、48MBTI模板、性格约束、认证系统
- 数据库：12表+30方向+8087岗位

### 第4轮：快速了解
- **状态：** complete
- API: GET /directions (30条), GET /directions/:id
- 前端: DirectionList(卡片网格), DirectionDetail(两栏)

### 第5轮：性格分析
- **状态：** complete
- API: GET /questions (40题), POST /submit, GET /result
- 规则引擎: 计分→类型判定→模板匹配
- 前端: 逐题作答+结果展示

### 第6轮：假数据
- **状态：** complete
- 创建: multimodal.py, general_llm.py, classifier.py, embedding.py, search.py, model_interface.py
- 11个FAKE_函数全部可用

### 第7轮：能力评估
- **状态：** ⚠️ 功能完成但缺frontend-design+codereview
- API: POST /upload, POST /describe, GET /portrait (全部200)
- 调用链: M1/M2-1→M4→M2-2/M2-3→写入DB+更新进度
- 前端: 双模式输入+ECharts雷达图

### 第8轮：岗位推荐
- **状态：** pending
- 待开始

## 测试结果
| 测试 | 输入 | 结果 |
|------|------|:--:|
| GET /questions | - | 40题 |
| POST /submit | 全A答案 | ESTJ 强度3 |
| GET /result | token | ESTJ已存 |
| POST /describe | 中文描述 | 72/78/65 |
| GET /portrait | token | 画像返回 |
| GET /directions | - | 30方向 |
| POST /register | 新用户 | token返回 |

## 错误日志
| 时间戳 | 错误 | 解决方案 |
|--------|------|---------|
| 16:55 | FK 3780 incompatible | 删库重建 |
| 16:57 | seed脚本GBK编码 | 替换特殊字符 |
| 17:01 | MBTI模板4条而非48条 | 用脚本重新生成 |
| 18:22 | bcrypt与passlib不兼容 | 直接调bcrypt |
| 22:35 | curl中文JSON编码 | 改用Python requests |
