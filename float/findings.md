# 发现与决策

## 技术决策
| 决策 | 理由 |
|------|------|
| FastAPI + SQLModel | 文档要求，异步支持，自带Swagger |
| React + Vite + Tailwind | 文档要求，开发快 |
| Framer Motion | 首页动画需求，暗色主题配合好 |
| ECharts | 雷达图需求 |
| bcrypt 直接调用而非 passlib | passlib 1.7.4 与 bcrypt 5.x 不兼容 |
| pymysql 而非 mysqlclient | Windows 免编译 |
| SQLModel.metadata.create_all() 而非 Alembic | 比赛项目无需生产级迁移 |
| 种子脚本先删positions再删directions | FK约束要求 |
| 登录守卫用 Navigate 组件而非路由拦截 | 简单可靠 |
| 统一 MODEL_MODE 开关而非独立开关 | 全量切换，管理简单 |

## 真实模型覆盖(第8.6-8.7轮)

| 编号 | 函数 | 模型 | 部署 |
|:---:|------|------|------|
| M1 | extract_from_pdf | ✅ qwen3.7-plus 多模态 | 阿里云百炼 (base64 PDF/图片) |
| M2-1 | extract_from_text | ✅ qwen3.7-plus | 阿里云百炼 |
| M2-2 | score_abilities | ✅ qwen3.7-plus | 阿里云百炼 |
| M2-3 | infer_soft_labels | ✅ Qwen2.5-7B | LM Studio 本地 |
| M2-4 | write_recommendation | ✅ qwen3.7-plus | 阿里云百炼 |
| M2-4ext | analyze_position_match | ✅ qwen3.7-plus | 阿里云百炼 |
| M2-5 | polish_report | ✅ qwen3.7-plus | 阿里云百炼 |
| M2-6 | chat_response | ✅ qwen3.7-plus | 阿里云百炼 |
| M3 | search_trends/resources | ✅ qwen3.7-plus + 联网 | 阿里云百炼 |
| M4 | classify_certificate/competition | ✅ Qwen2.5-7B | LM Studio 本地 |
| M5 | vectorize_and_match | ✅ bge-large-zh-v1.5 | Python 本地 |

## 第16轮：全链本地化 (2026-07-01)

### 决策
| 决策 | 理由 |
|------|------|
| 能力分析全链合并为一次本地 LLM 调用 | 原来百炼×2 + LM Studio×3~6，串行+并行混排，改为一次完成 |
| 岗位匹配分析本地化 | 对比用户画像和岗位要求，文本分析不需要联网 |
| 报告润色本地化 | 文本润色不需要联网 |
| 发展路径生成本地化 | 文本生成不需要联网，仅资源搜索保留百炼 |
| 百炼仅保留搜索功能 | 趋势搜索和资源搜索需要联网 |
| 对话收集改为汇总全部消息后分析 | 之前只传最后一条，前面信息白费 |
| 选 Qwen2.5-7B 而非 DeepSeek R1 | R1 推理链过长（53s vs 14s），打分归类不需要深度推理 |
| 前端对话暂存用 ref 而非 DB | 对话仅在当前会话有效，无需持久化 |

### 模型对比
| 模型 | 能力分析 | 岗位详情 | 结论 |
|------|:---:|:---:|------|
| Qwen2.5-7B-Instruct-1M | 13-14s | 9-10s | ✅ 采用 |
| DeepSeek R1 Distill 8B Q4 | 53.5s | 25.5s | ❌ 不适合 |
| Qwen2.5-7B Q4_K_M | 预期 8-10s | 预期 5-7s | 🔜 待验证 |

### 本地模型实测速度
| 函数 | 模型 | 耗时 |
|------|------|:---:|
| analyze_resume | LM Studio Qwen2.5-7B | 14.1s |
| infer_soft_labels | LM Studio Qwen2.5-7B | 4.2s |
| classify_certificate | LM Studio Qwen2.5-7B | 3.2s/个 |
| classify_competition | LM Studio Qwen2.5-7B | 2.9s/个 |

### 全流程基准 (纯本地)
注册 0.2s + MBTI 0s + 能力分析 13.2s + 岗位推荐 2.0s + 岗位详情 9.4s = **24.8s**

## 遇到的问题
| 问题 | 解决方案 |
|------|---------|
| FK类型不兼容(MySQL 3780) | 旧库有stage_inferences残留表干扰，删库重建 |
| seed脚本打印✓字符GBK报错 | 替换为ASCII [OK]标记 |
| MBTI模板JSON文件结构嵌套 | 模板在templates键下，需正确解析 |
| curl传中文JSON编码问题 | 改用Python requests测试 |
| Vite端口递增5173→5174→5175 | 加--strictPort，启动前taskkill清理 |
| 百炼 API 403 找不到模型 | 改用专属域名 ws-jacnkrr2eidonzn9.cn-beijing.maas.aliyuncs.com |
| HuggingFace 直连超时 | 用户开梯子后正常 |
| enable_search 30秒超时 | 调大到120秒 timeout |
| 前端白屏 ERR_CACHE_READ_FAILURE | 清除 node_modules/.vite 缓存 |
| /ability/describe 500 NameError | 误删 process_description 导入，已恢复 |
| 岗位详情 500 (position 3616) | analyze_position_match 超时，已本地化解决 |
