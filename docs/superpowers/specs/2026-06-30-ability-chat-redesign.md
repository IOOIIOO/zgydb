# 能力评估对话式重构 设计文档

> 状态: approved | 日期: 2026-06-30

## 目标

将 Ability.tsx 从传统的"上传简历 / 文字描述"双Tab页面重构为AI引导式对话界面。简历上传作为对话工具栏中的上传按钮。

## 交互模式

**AI引导式对话**：AI 主动按阶段提问（教育背景 → 技能工具 → 项目经验 → 证书竞赛），逐步收集信息，收集完成后自动生成能力画像。

### 对话阶段流转

```
greeting → ask_education → ask_skills → ask_projects → ask_certificates → analysis
```

用户可在任意阶段通过 📎 按钮上传简历，上传后跳过引导直接出画像。

## 布局方案

**上下分屏（C方案）**：
- 上方：结果展示区（雷达图 + 评分 + 优势短板），画像生成后显示，可折叠
- 下方：聊天消息流 + 输入框
- 两边独立滚动

## 架构

### 后端新增

| 项目 | 内容 |
|------|------|
| 接口 | `POST /api/v1/ability/chat` |
| 请求体 | `{ message: string, history: ChatMessage[] }` |
| 响应体 | `{ reply: string, stage: string, portrait_ready: bool }` |
| 假数据 | `FAKE_chat_response()` — 根据 stage 和用户输入返回引导提问或画像已就绪信号 |
| 文件 | `fake_data/general_llm.py` (新增函数), `routers/ability.py` (新增端点), `schemas/ability.py` (新增schema) |

### 前端变更

| 文件 | 操作 | 说明 |
|------|------|------|
| `components/ui/chat-messages.tsx` | 新建 | 消息气泡列表（AI/用户），支持画像卡片 |
| `components/ui/chat-input.tsx` | 新建 | 自适应输入框 + 📎上传按钮 + 发送按钮 |
| `pages/dashboard/Ability.tsx` | 重写 | 上下分屏布局，编排对话流程 |
| `api/ability.ts` | 修改 | 新增 `sendChatMessage()` |

### 数据流

```
用户输入 → POST /ability/chat { message, history }
         → FAKE_chat_response(stage, message)
         → 返回 { reply, stage, portrait_ready }
         → 前端追加AI消息到聊天流
         → 若 portrait_ready: 触发 GET /ability/portrait → 渲染上方结果区
```

### 组件Props接口

```typescript
// ChatMessages
interface ChatMessagesProps {
  messages: ChatMessage[];
  isTyping: boolean;
  onUploadClick: () => void;
}

// ChatMessage
interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  portrait?: AbilityPortrait; // 画像卡片数据，仅analysis阶段
}

// ChatInput
interface ChatInputProps {
  onSend: (text: string) => void;
  onFileSelect: (file: File) => void;
  disabled: boolean;
}
```

## 设计风格约束

- 参考 AnimatedAIChat 组件的玻璃态暗色风格
- 保持项目现有的 indigo/rose 渐变主色调
- 消息气泡：AI 左对齐半透明玻璃态，用户右对齐 indigo 调
- 输入框：底部固定，自适应高度（60-200px），聚焦时跟随鼠标的光晕效果
- 过渡动画：Framer Motion spring 动画
- 依赖：lucide-react、framer-motion（已安装）

## 假数据标注铁律

所有 `FAKE_` 前缀函数必须包含：
1. TODO 注释块（功能描述 + 替换模型类型 + 调用位置）
2. 函数名前缀 `FAKE_`
3. 通过 `model_interface.py` 中间层暴露
