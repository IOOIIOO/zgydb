# 能力评估对话式重构 实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 将 Ability.tsx 从双Tab页面重构为 AI 引导式对话界面，简历上传作为对话框工具栏按钮。

**Architecture:** 后端新增 POST /ability/chat 端点 + FAKE_chat_response 假数据，前端拆分为 ChatMessages + ChatInput 两个组件，Ability.tsx 编排上下分屏布局。

**Tech Stack:** FastAPI + SQLModel (后端), React + TypeScript + Tailwind + Framer Motion (前端)

## Global Constraints

- 所有假数据函数 MUST 以 FAKE_ 前缀命名，包含 TODO 注释块标注替换信息
- 所有 AI 调用 MUST 通过 model_interface.py 中间层
- 保持暗色玻璃态主题，匹配现有设计风格
- 依赖已安装：lucide-react, framer-motion, echarts

---

### Task 1: 后端 — FAKE_chat_response 假数据函数

**Files:**
- Modify: `backend/app/services/fake_data/general_llm.py` (追加函数)

**Interfaces:**
- Produces: `FAKE_chat_response(stage: str, user_message: str) -> dict` — 返回 `{ reply: str, next_stage: str, portrait_ready: bool }`
- Exported via: `model_interface.py` as `chat_response`

- [ ] **Step 1: 在 general_llm.py 末尾追加 FAKE_chat_response 函数**

```python
def FAKE_chat_response(stage: str, user_message: str) -> dict:
    """
    M2-6: AI 引导式对话回复，用于能力评估聊天流程。

    功能描述: 根据当前对话阶段和用户输入，返回 AI 的引导性回复。
             流转: greeting → ask_education → ask_skills → ask_projects → ask_certificates → analysis
             当用户上传简历文件时（stage="file_uploaded"），直接返回 portrait_ready=True。
    TODO: 替换为真实通用大模型（如 GPT-4 / DeepSeek / 文心一言 / 通义千问），
          传入完整对话历史和当前阶段，让模型自然地引导用户完成能力信息收集。
    预期模型类型: 通用大语言模型（LLM）
    调用位置: POST /ability/chat — 能力评估对话接口

    Args:
        stage: 当前对话阶段 (greeting | ask_education | ask_skills | ask_projects | ask_certificates | file_uploaded)
        user_message: 用户最新消息内容

    Returns:
        AI 回复文本、下一步阶段、画像是否就绪
    """
    replies = {
        "greeting": {
            "reply": "你好！我是你的 AI 能力评估助手 👋\n\n接下来我会问你几个问题，帮你全面分析能力画像。准备好了吗？\n\n首先，请告诉我你的**最高学历**是什么？（比如：本科、硕士、博士、大专等）",
            "next_stage": "ask_education",
            "portrait_ready": False,
        },
        "ask_education": {
            "reply": f"了解了，你的学历是 **{user_message}**。\n\n接下来，请告诉我你掌握哪些**技术技能和工具**？比如编程语言、框架、办公软件等，越详细越好。",
            "next_stage": "ask_skills",
            "portrait_ready": False,
        },
        "ask_skills": {
            "reply": f"技能很全面！这些工具能力在职场上很有竞争力 💪\n\n再来说说你做过的**项目经历**吧。可以是课程设计、竞赛项目、实习项目等，描述一下你负责的内容和用到的技术。",
            "next_stage": "ask_projects",
            "portrait_ready": False,
        },
        "ask_projects": {
            "reply": "很有价值的项目经验！这些实践经历对求职帮助很大。\n\n最后一个问题：你是否有**证书或竞赛经历**？英语等级、计算机等级、专业技能认证、数学建模等都可以。",
            "next_stage": "ask_certificates",
            "portrait_ready": False,
        },
        "ask_certificates": {
            "reply": "信息收集完毕！我正在根据你提供的信息生成能力画像，请稍等... 🎯",
            "next_stage": "analysis",
            "portrait_ready": True,
        },
        "file_uploaded": {
            "reply": "简历已收到！我正在分析你的简历内容并生成能力画像，请稍等... 📄✨",
            "next_stage": "analysis",
            "portrait_ready": True,
        },
    }
    return replies.get(stage, replies["greeting"])
```

- [ ] **Step 2: 在 model_interface.py 中添加导出**

在 `backend/app/services/model_interface.py`：

```python
# 在 general_llm 导入块中添加 FAKE_chat_response
from app.services.fake_data.general_llm import (
    # ... 现有导入保持不变 ...
    FAKE_chat_response,
)

# 在导出别名区域添加
chat_response = FAKE_chat_response
```

- [ ] **Step 3: 验证 — 快速 Python 测试**

```bash
cd d:\zgyd\backend && python -c "from app.services.fake_data.general_llm import FAKE_chat_response; r = FAKE_chat_response('greeting', ''); print(r['reply'][:50]); assert r['next_stage'] == 'ask_education'; assert not r['portrait_ready']; print('[OK]')"
```

Expected: 打印 AI 欢迎语前50字 + `[OK]`

---

### Task 2: 后端 — Chat 请求/响应 Schema + 端点

**Files:**
- Modify: `backend/app/schemas/ability.py` (追加 schema)
- Modify: `backend/app/routers/ability.py` (追加端点)

**Interfaces:**
- Consumes: `chat_response(stage, message)` from model_interface
- Produces: `POST /api/v1/ability/chat` — 请求 `{ message, stage }` → 响应 `{ reply, next_stage, portrait_ready }`

- [ ] **Step 1: 在 schemas/ability.py 末尾追加 ChatRequest / ChatResponse**

```python
class ChatRequest(BaseModel):
    """对话消息请求"""
    message: str
    stage: str = "greeting"  # 当前对话阶段


class ChatResponse(BaseModel):
    """对话消息响应"""
    reply: str
    next_stage: str
    portrait_ready: bool = False
```

- [ ] **Step 2: 在 routers/ability.py 末尾追加 chat 端点**

```python
from app.schemas.ability import ChatRequest, ChatResponse
from app.services.model_interface import chat_response


@router.post("/chat", response_model=ChatResponse)
def chat(
    body: ChatRequest,
    current_user: UserResponse = Depends(_get_current_user),
    session: Session = Depends(get_session),
):
    """AI 引导式对话：接收用户消息，返回 AI 回复

    前端按 stage 顺序调用：
    greeting → ask_education → ask_skills → ask_projects → ask_certificates → analysis

    当 stage="file_uploaded" 时，直接返回 portrait_ready=True
    """
    result = chat_response(body.stage, body.message)

    # 如果画像就绪，触发后台画像生成（复用 _build_portrait 逻辑）
    if result["portrait_ready"]:
        from app.services.ability_service import process_description
        # 用收集到的对话内容生成画像
        try:
            process_description(session, current_user.id, body.message)
        except Exception:
            pass  # 假数据阶段不阻塞，即使生成失败也返回就绪信号

    return ChatResponse(
        reply=result["reply"],
        next_stage=result["next_stage"],
        portrait_ready=result["portrait_ready"],
    )
```

- [ ] **Step 3: 验证 — curl 测试端点**

```bash
curl -s -X POST http://localhost:8001/api/v1/ability/chat -H "Content-Type: application/json" -H "Authorization: Bearer <token>" -d '{"message":"","stage":"greeting"}' | python -c "import sys,json; d=json.load(sys.stdin); print(d['reply'][:60]); assert 'next_stage' in d; print('[OK]')"
```

Expected: 打印 AI 回复前60字 + `[OK]`

---

### Task 3: 前端 — ChatMessages 消息气泡组件

**Files:**
- Create: `frontend/src/components/ui/chat-messages.tsx`

**Interfaces:**
- Consumes: `AbilityPortrait` from types
- Produces: `<ChatMessages messages={ChatMessage[]} isTyping={boolean} />`

- [ ] **Step 1: 创建组件文件**

```tsx
"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Bot, User, FileText } from "lucide-react";
import type { AbilityPortrait } from "@/types";
import { cn } from "@/lib/utils";

export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
  portrait?: AbilityPortrait;
}

interface ChatMessagesProps {
  messages: ChatMessage[];
  isTyping: boolean;
}

function TypingDots() {
  return (
    <div className="flex items-center gap-1 px-4 py-3">
      {[1, 2, 3].map((dot) => (
        <motion.div
          key={dot}
          className="w-2 h-2 bg-white/30 rounded-full"
          initial={{ opacity: 0.2 }}
          animate={{ opacity: [0.2, 0.8, 0.2], scale: [0.8, 1.1, 0.8] }}
          transition={{ duration: 1.2, repeat: Infinity, delay: dot * 0.15, ease: "easeInOut" }}
        />
      ))}
    </div>
  );
}

export function ChatMessages({ messages, isTyping }: ChatMessagesProps) {
  return (
    <div className="flex flex-col gap-4">
      <AnimatePresence>
        {messages.map((msg) => (
          <motion.div
            key={msg.id}
            initial={{ opacity: 0, y: 12, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            transition={{ duration: 0.25, ease: "easeOut" }}
            className={cn("flex gap-3", msg.role === "user" ? "justify-end" : "justify-start")}
          >
            {/* AI 头像 */}
            {msg.role === "ai" && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mt-0.5">
                <Bot className="w-4 h-4 text-indigo-400/60" />
              </div>
            )}

            {/* 消息气泡 */}
            <div
              className={cn(
                "max-w-[80%] rounded-2xl px-4 py-3 text-sm leading-relaxed",
                msg.role === "ai"
                  ? "bg-white/[0.03] border border-white/[0.06] text-white/70 rounded-tl-md"
                  : "bg-indigo-500/[0.12] border border-indigo-500/20 text-white/80 rounded-tr-md"
              )}
            >
              <p className="whitespace-pre-wrap">{msg.content}</p>
            </div>

            {/* 用户头像 */}
            {msg.role === "user" && (
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mt-0.5">
                <User className="w-4 h-4 text-white/40" />
              </div>
            )}
          </motion.div>
        ))}
      </AnimatePresence>

      {/* AI 正在输入 */}
      <AnimatePresence>
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 8 }}
            className="flex gap-3"
          >
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mt-0.5">
              <Bot className="w-4 h-4 text-indigo-400/60" />
            </div>
            <div className="bg-white/[0.03] border border-white/[0.06] rounded-2xl rounded-tl-md">
              <TypingDots />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd d:\zgyd\frontend && npx tsc --noEmit 2>&1 | head -20
```

Expected: No errors related to chat-messages.tsx

---

### Task 4: 前端 — ChatInput 输入框组件

**Files:**
- Create: `frontend/src/components/ui/chat-input.tsx`

**Interfaces:**
- Consumes: None external
- Produces: `<ChatInput onSend={fn} onFileSelect={fn} disabled={bool} />`

- [ ] **Step 1: 创建组件文件**

```tsx
"use client";

import { useRef, useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";
import { Send, Paperclip, Upload, Loader2 } from "lucide-react";
import { cn } from "@/lib/utils";

interface ChatInputProps {
  onSend: (text: string) => void;
  onFileSelect: (file: File) => void;
  disabled?: boolean;
  uploading?: boolean;
}

function useAutoResizeTextarea(minHeight: number, maxHeight: number) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const adjustHeight = useCallback(
    (reset?: boolean) => {
      const textarea = textareaRef.current;
      if (!textarea) return;
      if (reset) {
        textarea.style.height = `${minHeight}px`;
        return;
      }
      textarea.style.height = `${minHeight}px`;
      const newHeight = Math.max(minHeight, Math.min(textarea.scrollHeight, maxHeight));
      textarea.style.height = `${newHeight}px`;
    },
    [minHeight, maxHeight]
  );

  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) textarea.style.height = `${minHeight}px`;
  }, [minHeight]);

  return { textareaRef, adjustHeight };
}

export function ChatInput({ onSend, onFileSelect, disabled, uploading }: ChatInputProps) {
  const [value, setValue] = useState("");
  const { textareaRef, adjustHeight } = useAutoResizeTextarea(60, 200);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(trimmed);
    setValue("");
    adjustHeight(true);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileSelect(file);
      // 重置 input 以便重复选择同一文件
      e.target.value = "";
    }
  };

  return (
    <div className="relative backdrop-blur-2xl bg-white/[0.015] rounded-2xl border border-white/[0.06]">
      {/* 输入区域 */}
      <div className="p-4">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => {
            setValue(e.target.value);
            adjustHeight();
          }}
          onKeyDown={handleKeyDown}
          placeholder="输入你的回答... (Enter 发送，Shift+Enter 换行)"
          disabled={disabled}
          className={cn(
            "w-full px-4 py-3",
            "resize-none",
            "bg-transparent",
            "border-none",
            "text-white/80 text-sm",
            "focus:outline-none",
            "placeholder:text-white/15",
            "min-h-[60px]"
          )}
          style={{ overflow: "hidden" }}
        />
      </div>

      {/* 工具栏 */}
      <div className="px-4 pb-4 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          {/* 文件上传按钮 */}
          <motion.button
            type="button"
            whileTap={{ scale: 0.94 }}
            onClick={() => fileInputRef.current?.click()}
            disabled={disabled || uploading}
            className="p-2 text-white/30 hover:text-white/70 rounded-lg transition-colors relative group disabled:opacity-30"
            title="上传简历文件"
          >
            {uploading ? (
              <Loader2 className="w-4 h-4 animate-spin" />
            ) : (
              <Upload className="w-4 h-4" />
            )}
            <motion.span
              className="absolute inset-0 bg-white/[0.05] rounded-lg opacity-0 group-hover:opacity-100 transition-opacity"
              layoutId="input-btn-highlight"
            />
          </motion.button>
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={handleFileChange}
            className="hidden"
          />
        </div>

        {/* 发送按钮 */}
        <motion.button
          type="button"
          onClick={handleSend}
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.97 }}
          disabled={disabled || !value.trim()}
          className={cn(
            "px-5 py-2 rounded-xl text-sm font-medium transition-all flex items-center gap-2",
            value.trim() && !disabled
              ? "bg-white text-[#0A0A0B] shadow-lg shadow-white/5"
              : "bg-white/[0.04] text-white/25 cursor-not-allowed"
          )}
        >
          <Send className="w-3.5 h-3.5" />
          <span>发送</span>
        </motion.button>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd d:\zgyd\frontend && npx tsc --noEmit 2>&1 | head -20
```

Expected: No errors related to chat-input.tsx

---

### Task 5: 前端 — API 层新增 sendChatMessage

**Files:**
- Modify: `frontend/src/api/ability.ts`

**Interfaces:**
- Produces: `sendChatMessage(message: string, stage: string) => Promise<ChatResponse>`

- [ ] **Step 1: 添加 API 函数和类型**

在 `frontend/src/api/ability.ts` 中追加：

```typescript
/** 对话响应 */
export interface ChatResponse {
  reply: string;
  next_stage: string;
  portrait_ready: boolean;
}

/** 发送对话消息 */
export function sendChatMessage(message: string, stage: string): Promise<ChatResponse> {
  return client.post("/ability/chat", { message, stage });
}
```

---

### Task 6: 前端 — 重写 Ability.tsx 对话界面

**Files:**
- Modify: `frontend/src/pages/dashboard/Ability.tsx` (重写大部分)

**Interfaces:**
- Consumes: `sendChatMessage`, `uploadResume`, `getAbilityPortrait` from api/ability
- Consumes: `ChatMessages`, `ChatInput` from components/ui
- Produces: 上下分屏对话式能力评估页面

- [ ] **Step 1: 完整重写 Ability.tsx**

```tsx
import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as echarts from "echarts";
import { CheckCircle2, RotateCcw, ArrowRight, ChevronDown, ChevronUp } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ChatMessages, type ChatMessage } from "@/components/ui/chat-messages";
import { ChatInput } from "@/components/ui/chat-input";
import { sendChatMessage, uploadResume, getAbilityPortrait } from "@/api/ability";
import type { AbilityPortrait } from "@/types";

export default function Ability() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [stage, setStage] = useState("greeting");
  const [isTyping, setIsTyping] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [portrait, setPortrait] = useState<AbilityPortrait | null>(null);
  const [resultExpanded, setResultExpanded] = useState(true);
  const [error, setError] = useState("");
  const chartRef = useRef<HTMLDivElement>(null);
  const msgId = useRef(0);

  // 初始化：检查已有画像 + 发送 AI 欢迎语
  useEffect(() => {
    getAbilityPortrait()
      .then((p) => {
        setPortrait(p);
        setStage("analysis");
      })
      .catch(() => {
        // 没有画像，启动对话
        addMessage("ai", "");
        sendAiMessage("greeting", "");
      });
  }, []);

  // 雷达图渲染
  useEffect(() => {
    if (!portrait || !chartRef.current || !resultExpanded) return;
    const chart = echarts.init(chartRef.current);
    chart.setOption({
      radar: {
        center: ["50%", "50%"], radius: "70%",
        indicator: [
          { name: "知识", max: 100 }, { name: "工具", max: 100 }, { name: "项目", max: 100 },
          { name: "逻辑", max: 100 }, { name: "沟通", max: 100 }, { name: "学习", max: 100 },
        ],
        axisName: { color: "rgba(255,255,255,0.3)", fontSize: 11 },
        splitArea: { areaStyle: { color: ["rgba(255,255,255,0.015)", "rgba(255,255,255,0.008)"] } },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } },
        axisLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
      },
      series: [{
        type: "radar", symbol: "none",
        data: [{
          value: [
            portrait.knowledge_score, portrait.tool_score, portrait.project_score,
            _labelScore(portrait.logic_label), _labelScore(portrait.communication_label),
            _labelScore(portrait.learning_label),
          ],
          name: "能力画像",
          areaStyle: { color: "rgba(99,102,241,0.12)" },
          lineStyle: { color: "rgba(129,140,248,0.5)", width: 2 },
        }],
      }],
    });
    return () => chart.dispose();
  }, [portrait, resultExpanded]);

  const addMessage = useCallback((role: "user" | "ai", content: string, portraitData?: AbilityPortrait) => {
    msgId.current += 1;
    setMessages((prev) => [...prev, { id: String(msgId.current), role, content, portrait: portraitData }]);
  }, []);

  const sendAiMessage = useCallback(async (currentStage: string, userMessage: string) => {
    setIsTyping(true);
    try {
      const res = await sendChatMessage(userMessage, currentStage);
      // 小延迟让 typing 动画可见
      await new Promise((r) => setTimeout(r, 800));
      setIsTyping(false);
      addMessage("ai", res.reply);
      setStage(res.next_stage);

      if (res.portrait_ready) {
        // 拉取生成的画像
        try {
          const p = await getAbilityPortrait();
          setPortrait(p);
        } catch {
          // 假数据阶段可能还没写入，稍后重试
        }
      }
    } catch {
      setIsTyping(false);
      setError("对话请求失败，请重试");
    }
  }, [addMessage]);

  const handleSend = useCallback((text: string) => {
    setError("");
    addMessage("user", text);
    sendAiMessage(stage, text);
  }, [stage, addMessage, sendAiMessage]);

  const handleFileSelect = useCallback(async (file: File) => {
    setError("");
    setUploading(true);
    addMessage("user", `[上传了简历文件: ${file.name}]`);
    try {
      await uploadResume(file);
      setUploading(false);
      // 上传成功后走 file_uploaded 阶段，直接出画像
      await sendAiMessage("file_uploaded", file.name);
    } catch {
      setUploading(false);
      setError("简历上传失败，请重试");
    }
  }, [addMessage, sendAiMessage]);

  const handleReset = () => {
    setMessages([]);
    setStage("greeting");
    setPortrait(null);
    setError("");
    msgId.current = 0;
    addMessage("ai", "");
    sendAiMessage("greeting", "");
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-120px)] flex flex-col">
      {/* 标题栏 */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="mb-6 flex-shrink-0">
        <h1 className="text-3xl font-bold">
          <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">能力评估</span>
        </h1>
        <p className="text-white/35 mt-2">与 AI 助手对话，逐步完成能力画像分析</p>
      </motion.div>

      {/* 错误提示 */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="mb-4 p-3 rounded-xl bg-rose-500/[0.04] border border-rose-500/[0.1] text-rose-400/80 text-sm flex-shrink-0"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* 结果展示区（画像生成后显示） */}
      <AnimatePresence>
        {portrait && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: resultExpanded ? "auto" : 48 }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3 }}
            className="flex-shrink-0 mb-4 overflow-hidden"
          >
            <div className="p-4 rounded-2xl bg-white/[0.015] border border-white/[0.06]">
              {/* 折叠头部 */}
              <button
                onClick={() => setResultExpanded(!resultExpanded)}
                className="w-full flex items-center justify-between text-sm"
              >
                <span className="text-white/50 font-semibold flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-400/60" />
                  能力画像结果
                </span>
                {resultExpanded ? (
                  <ChevronUp className="w-4 h-4 text-white/30" />
                ) : (
                  <ChevronDown className="w-4 h-4 text-white/30" />
                )}
              </button>

              {resultExpanded && (
                <div className="mt-4 grid grid-cols-1 lg:grid-cols-5 gap-4">
                  {/* 雷达图 */}
                  <div className="lg:col-span-3">
                    <div ref={chartRef} style={{ width: "100%", height: 280 }} />
                  </div>
                  {/* 评分 */}
                  <div className="lg:col-span-2 space-y-3">
                    {[
                      { label: "知识储备", score: portrait.knowledge_score, color: "from-indigo-500 to-indigo-400" },
                      { label: "工具技能", score: portrait.tool_score, color: "from-cyan-500 to-cyan-400" },
                      { label: "项目经验", score: portrait.project_score, color: "from-amber-500 to-amber-400" },
                    ].map((d) => (
                      <div key={d.label}>
                        <div className="flex justify-between text-xs mb-1">
                          <span className="text-white/35">{d.label}</span>
                          <span className="text-white/55 font-mono">{d.score}</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${d.score}%` }}
                            transition={{ duration: 0.7, ease: "easeOut" }}
                            className={`h-full rounded-full bg-gradient-to-r ${d.color}`}
                          />
                        </div>
                      </div>
                    ))}
                    {/* 软标签 */}
                    <div className="pt-3 border-t border-white/[0.04] grid grid-cols-2 gap-2">
                      {[
                        { k: "logic_label", label: "逻辑思维" },
                        { k: "communication_label", label: "沟通协作" },
                        { k: "learning_label", label: "学习能力" },
                      ].map(({ k, label }) => (
                        <div key={k} className="flex items-center gap-2 text-xs">
                          <CheckCircle2 className="w-3 h-3 text-emerald-400/50 flex-shrink-0" />
                          <span className="text-white/25">{label}</span>
                          <span className="text-white/50">{(portrait as any)[k]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* 聊天区域 */}
      <div className="flex-1 overflow-y-auto mb-4 min-h-0">
        <ChatMessages messages={messages} isTyping={isTyping} />
      </div>

      {/* 输入框区域 */}
      <div className="flex-shrink-0 pb-6">
        <ChatInput
          onSend={handleSend}
          onFileSelect={handleFileSelect}
          disabled={isTyping || stage === "analysis"}
          uploading={uploading}
        />

        {/* 底部操作 */}
        {portrait && (
          <div className="flex items-center justify-center gap-4 mt-4">
            <button
              onClick={handleReset}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white/[0.02] border border-white/[0.06] text-white/25 text-sm hover:bg-white/[0.05] hover:text-white/45 transition-all"
            >
              <RotateCcw className="w-3.5 h-3.5" /> 重新评估
            </button>
            <button
              onClick={() => navigate("/dashboard/direction")}
              className="inline-flex items-center gap-2 px-5 py-2 rounded-full bg-white text-[#030303] font-semibold text-sm hover:bg-white/90 transition-all"
            >
              下一步：方向选择 <ArrowRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>
    </div>
  );
}

function _labelScore(label: string): number {
  return (
    { "优秀": 85, "突出": 90, "强": 85, "较强": 80, "良好": 70, "中等": 50, "一般": 35, "较弱": 20 }[label] || 50
  );
}
```

- [ ] **Step 2: TypeScript 编译检查**

```bash
cd d:\zgyd\frontend && npx tsc --noEmit 2>&1 | head -30
```

Expected: No TypeScript errors

- [ ] **Step 3: 启动前端验证页面渲染**

```bash
cd d:\zgyd\frontend && npx vite --host 0.0.0.0
```

打开 `/dashboard/ability`，确认：
- AI 自动发送欢迎语
- 用户输入后 AI 引导下一个问题
- 上传按钮可触发文件选择
- 对话完成后上方显示雷达图

---

### Task 7: 集成验证 — 全流程端到端测试

- [ ] **Step 1: 启动后端（端口 8001）**

```bash
cd d:\zgyd\backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

- [ ] **Step 2: 测试 chat 端点完整流程**

```bash
python -c "
import requests, json
BASE = 'http://localhost:8001/api/v1/ability'
# 先注册登录获取 token
s = requests.Session()
# 使用已有测试账号
r = s.post('http://localhost:8001/api/v1/auth/login', json={'username_or_email': 'test', 'password': 'test123'})
token = r.json().get('access_token', '')
headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}

# 完整对话流程
stages = [('greeting', ''), ('ask_education', '本科'), ('ask_skills', 'Python, SQL, Docker'),
          ('ask_projects', '做了一个电商系统'), ('ask_certificates', '英语六级')]
for stage, msg in stages:
    r = s.post(f'{BASE}/chat', json={'message': msg, 'stage': stage}, headers=headers)
    d = r.json()
    print(f'[{stage}] → next: {d[\"next_stage\"]}, portrait: {d[\"portrait_ready\"]}')
    assert r.status_code == 200
print('[OK] 全部5阶段对话通过')
"
```

Expected: 5个阶段全部 200，最后一个返回 `portrait_ready: true`

- [ ] **Step 3: 更新 task_plan.md 和 progress.md**

记录第 8.6 轮完成状态。

---

## 文件变更汇总

| 文件 | 操作 | 任务 |
|------|------|------|
| `backend/app/services/fake_data/general_llm.py` | 追加 ~60行 | Task 1 |
| `backend/app/services/model_interface.py` | +2行 | Task 1 |
| `backend/app/schemas/ability.py` | 追加 ~12行 | Task 2 |
| `backend/app/routers/ability.py` | 追加 ~30行 | Task 2 |
| `frontend/src/components/ui/chat-messages.tsx` | 新建 ~90行 | Task 3 |
| `frontend/src/components/ui/chat-input.tsx` | 新建 ~120行 | Task 4 |
| `frontend/src/api/ability.ts` | 追加 ~10行 | Task 5 |
| `frontend/src/pages/dashboard/Ability.tsx` | 重写 ~220行 | Task 6 |
