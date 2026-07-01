import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import * as echarts from "echarts";
import { CheckCircle2, RotateCcw, ArrowRight, ChevronDown, ChevronUp, Sparkles } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { ChatMessages, type ChatMessage } from "@/components/ui/chat-messages";
import { ChatInput } from "@/components/ui/chat-input";
import { sendChatMessage, uploadResume, getAbilityPortrait, submitDescription } from "@/api/ability";
import type { AbilityPortrait } from "@/types";
import { useAuth } from "@/hooks/useAuth";
import { clearUserDetails } from "@/lib/positionDetailCache";

export default function Ability() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [stage, setStage] = useState("greeting");
  const [isTyping, setIsTyping] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [portrait, setPortrait] = useState<AbilityPortrait | null>(null);
  const [resultExpanded, setResultExpanded] = useState(true);
  const [error, setError] = useState("");
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const chartRef = useRef<HTMLDivElement>(null);
  const msgId = useRef(0);
  const hasChecked = useRef(false);
  const chatScrollRef = useRef<HTMLDivElement>(null);
  const userMessagesRef = useRef<string[]>([]);

  // 鼠标追踪（全局光晕）
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

  // 自动滚动到底部（消息变化 / 结果面板出现时均触发）
  useEffect(() => {
    // 用 setTimeout 匹配结果面板的展开动画时长 (350ms)，确保布局稳定后再滚动
    const timer = setTimeout(() => {
      if (chatScrollRef.current) {
        chatScrollRef.current.scrollTo({
          top: chatScrollRef.current.scrollHeight,
          behavior: "smooth",
        });
      }
    }, portrait ? 400 : 50); // 面板出现时等动画完成，普通消息即时滚
    return () => clearTimeout(timer);
  }, [messages, isTyping, portrait, resultExpanded]);

  // 初始化：检查已有画像 + 发送 AI 欢迎语
  useEffect(() => {
    if (hasChecked.current) return;
    hasChecked.current = true;
    getAbilityPortrait()
      .then((p) => {
        if (p) { setPortrait(p); setStage("analysis"); }
        else { addMessage("ai", ""); sendAiMessage("greeting", ""); }
      })
      .catch(() => {
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
        center: ["50%", "50%"],
        radius: "70%",
        indicator: [
          { name: "知识", max: 100 },
          { name: "工具", max: 100 },
          { name: "项目", max: 100 },
          { name: "逻辑", max: 100 },
          { name: "沟通", max: 100 },
          { name: "学习", max: 100 },
        ],
        axisName: { color: "rgba(255,255,255,0.3)", fontSize: 11 },
        splitArea: {
          areaStyle: {
            color: ["rgba(255,255,255,0.015)", "rgba(255,255,255,0.008)"],
          },
        },
        splitLine: { lineStyle: { color: "rgba(255,255,255,0.05)" } },
        axisLine: { lineStyle: { color: "rgba(255,255,255,0.06)" } },
      },
      series: [
        {
          type: "radar",
          symbol: "none",
          data: [
            {
              value: [
                portrait.knowledge_score,
                portrait.tool_score,
                portrait.project_score,
                _labelScore(portrait.logic_label),
                _labelScore(portrait.communication_label),
                _labelScore(portrait.learning_label),
              ],
              name: "能力画像",
              areaStyle: { color: "rgba(99,102,241,0.12)" },
              lineStyle: { color: "rgba(129,140,248,0.5)", width: 2 },
            },
          ],
        },
      ],
    });
    return () => chart.dispose();
  }, [portrait, resultExpanded]);

  const addMessage = useCallback((role: "user" | "ai", content: string) => {
    msgId.current += 1;
    setMessages((prev) => [...prev, { id: String(msgId.current), role, content }]);
  }, []);

  const sendAiMessage = useCallback(
    async (currentStage: string, userMessage: string) => {
      setIsTyping(true);
      try {
        const res = await sendChatMessage(userMessage, currentStage);
        setIsTyping(false);
        addMessage("ai", res.reply);
        setStage(res.next_stage);

        if (res.portrait_ready) {
          // 汇总全部用户消息，一次性发送给本地模型分析
          const allText = [...userMessagesRef.current, userMessage].join("\n");
          if (allText.length >= 20) {
            try {
              addMessage("ai", "🔍 正在综合分析你的全部对话内容，生成能力画像...");
              await submitDescription(allText);
              if (user?.id) clearUserDetails(user.id);
              const p = await getAbilityPortrait();
              setPortrait(p);
              addMessage("ai", "✅ 能力画像已生成！你可以在上方查看雷达图和详细评分。");
            } catch {
              setError("画像生成失败，请点击「生成雷达图」按钮重试");
            }
          }
        }
      } catch {
        setIsTyping(false);
        setError("对话请求失败，请重试");
      }
    },
    [addMessage]
  );

  const handleSend = useCallback(
    (text: string) => {
      setError("");
      userMessagesRef.current.push(text);
      addMessage("user", text);
      sendAiMessage(stage, text);
    },
    [stage, addMessage, sendAiMessage]
  );

  const handleFileSelect = useCallback(
    async (file: File) => {
      setError("");
      setUploading(true);
      addMessage("ai", "📄 正在解析你的简历，提取教育背景、技能和项目经历...");
      addMessage("user", `[上传了简历: ${file.name}]`);
      try {
        await uploadResume(file);
        if (user?.id) clearUserDetails(user.id);
        setUploading(false);
        setIsTyping(true);
        try {
          const p = await getAbilityPortrait();
          setIsTyping(false);
          setPortrait(p);
          setStage("analysis");
          addMessage("ai", "✅ 简历解析完成！能力画像已生成，你可以在上方查看雷达图和详细评分。");
        } catch {
          setIsTyping(false);
          setError("画像获取失败，请稍后重试");
        }
      } catch {
        setUploading(false);
        setError("简历上传失败，请重试");
      }
    },
    [addMessage]
  );

  const handleGeneratePortrait = useCallback(async () => {
    const userMessages = messages
      .filter((m) => m.role === "user" && m.content)
      .map((m) => m.content)
      .join("\n");
    if (userMessages.length < 20) {
      setError("请先输入至少 20 个字的描述信息");
      return;
    }
    setError("");
    setIsTyping(true);
    addMessage("ai", "🔍 正在根据你的对话内容分析能力画像...");
    try {
      await submitDescription(userMessages);
      if (user?.id) clearUserDetails(user.id);
      setIsTyping(false);
      const p = await getAbilityPortrait();
      setPortrait(p);
      setStage("analysis");
      addMessage("ai", "✅ 能力画像已生成！你可以在上方查看雷达图和详细评分。");
    } catch {
      setIsTyping(false);
      setError("画像生成失败，请重试或继续对话");
    }
  }, [messages, addMessage]);

  const handleReset = () => {
    setMessages([]);
    setStage("greeting");
    setPortrait(null);
    setError("");
    msgId.current = 0;
    userMessagesRef.current = [];
    addMessage("ai", "");
    sendAiMessage("greeting", "");
  };

  return (
    <div className="max-w-4xl mx-auto h-[calc(100vh-100px)] flex flex-col relative">
      {/* ====== 环境光晕 ====== */}
      <div className="absolute inset-0 w-full h-full overflow-hidden pointer-events-none">
        <div className="absolute -top-32 left-1/4 w-96 h-96 bg-violet-500/[0.07] rounded-full mix-blend-normal filter blur-[128px] animate-pulse" />
        <div className="absolute bottom-12 right-1/4 w-96 h-96 bg-indigo-500/[0.06] rounded-full mix-blend-normal filter blur-[128px] animate-pulse" style={{ animationDelay: "700ms" }} />
        <div className="absolute top-1/3 -right-12 w-64 h-64 bg-fuchsia-500/[0.05] rounded-full mix-blend-normal filter blur-[96px] animate-pulse" style={{ animationDelay: "1000ms" }} />
      </div>

      {/* 全局鼠标光晕 */}
      <motion.div
        className="fixed w-[45rem] h-[45rem] rounded-full pointer-events-none z-0 opacity-[0.018] bg-gradient-to-r from-violet-500 via-fuchsia-500 to-indigo-500 blur-[96px]"
        animate={{
          x: mousePosition.x - 360,
          y: mousePosition.y - 360,
        }}
        transition={{
          type: "spring",
          damping: 30,
          stiffness: 100,
          mass: 0.6,
        }}
      />

      {/* ====== 标题 ====== */}
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="mb-5 flex-shrink-0 relative z-10"
      >
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500/15 to-violet-500/10 border border-indigo-500/15 flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.08)]">
            <Sparkles className="w-5 h-5 text-indigo-400/70" />
          </div>
          <div>
            <h1 className="text-2xl font-bold">
              <span className="bg-clip-text text-transparent bg-gradient-to-r from-white/95 to-white/70">
                能力评估
              </span>
            </h1>
            <p className="text-white/30 text-sm mt-0.5">
              与 AI 助手对话，逐步完成能力画像分析
            </p>
          </div>
        </div>
      </motion.div>

      {/* ====== 错误提示 ====== */}
      <AnimatePresence>
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="mb-4 p-3 rounded-xl bg-rose-500/[0.05] backdrop-blur-md border border-rose-500/[0.12] text-rose-400/80 text-sm flex-shrink-0 relative z-10"
          >
            {error}
          </motion.div>
        )}
      </AnimatePresence>

      {/* ====== 结果面板（画像就绪后显示） ====== */}
      <AnimatePresence>
        {portrait && (
          <motion.div
            initial={{ opacity: 0, height: 0, scale: 0.98 }}
            animate={{
              opacity: 1,
              height: resultExpanded ? "auto" : 48,
              scale: 1,
            }}
            exit={{ opacity: 0, height: 0, scale: 0.98 }}
            transition={{ duration: 0.35, ease: "easeOut" }}
            className="flex-shrink-0 mb-4 overflow-hidden relative z-10"
          >
            <div className="p-4 rounded-2xl bg-white/[0.018] backdrop-blur-xl border border-white/[0.06] shadow-[0_4px_32px_rgba(0,0,0,0.2)]">
              {/* 折叠头部 */}
              <button
                onClick={() => setResultExpanded(!resultExpanded)}
                className="w-full flex items-center justify-between text-sm group"
              >
                <span className="text-white/55 font-semibold flex items-center gap-2">
                  <motion.div
                    initial={{ rotate: 0 }}
                    animate={{ rotate: resultExpanded ? 0 : -90 }}
                    className="w-5 h-5 rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center"
                  >
                    <CheckCircle2 className="w-3 h-3 text-emerald-400/70" />
                  </motion.div>
                  能力画像结果
                </span>
                <motion.div
                  animate={{ rotate: resultExpanded ? 0 : 180 }}
                  className="text-white/25 group-hover:text-white/45 transition-colors"
                >
                  <ChevronUp className="w-4 h-4" />
                </motion.div>
              </button>

              {resultExpanded && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.1 }}
                  className="mt-4 grid grid-cols-1 lg:grid-cols-5 gap-5"
                >
                  {/* 雷达图 */}
                  <div className="lg:col-span-3">
                    <div ref={chartRef} style={{ width: "100%", height: 280 }} />
                  </div>
                  {/* 评分区 */}
                  <div className="lg:col-span-2 space-y-3.5">
                    {[
                      { label: "知识储备", score: portrait.knowledge_score, color: "from-indigo-400 to-indigo-300" },
                      { label: "工具技能", score: portrait.tool_score, color: "from-cyan-400 to-cyan-300" },
                      { label: "项目经验", score: portrait.project_score, color: "from-amber-400 to-amber-300" },
                    ].map((d) => (
                      <div key={d.label}>
                        <div className="flex justify-between text-xs mb-1.5">
                          <span className="text-white/30">{d.label}</span>
                          <span className="text-white/55 font-mono text-xs">{d.score}</span>
                        </div>
                        <div className="h-1.5 rounded-full bg-white/[0.04] overflow-hidden">
                          <motion.div
                            initial={{ width: 0 }}
                            animate={{ width: `${d.score}%` }}
                            transition={{ duration: 0.8, ease: "easeOut", delay: 0.15 }}
                            className={`h-full rounded-full bg-gradient-to-r ${d.color}`}
                          />
                        </div>
                      </div>
                    ))}
                    {/* 软标签 */}
                    <div className="pt-3.5 border-t border-white/[0.04] grid grid-cols-2 gap-2">
                      {[
                        { k: "logic_label", label: "逻辑思维" },
                        { k: "communication_label", label: "沟通协作" },
                        { k: "learning_label", label: "学习能力" },
                      ].map(({ k, label }) => (
                        <div key={k} className="flex items-center gap-2 text-xs">
                          <div className="w-1 h-1 rounded-full bg-emerald-400/40 flex-shrink-0" />
                          <span className="text-white/25">{label}</span>
                          <span className="text-white/50">{(portrait as any)[k]}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ====== 聊天消息区 ====== */}
      <div
        ref={chatScrollRef}
        className="flex-1 overflow-y-auto mb-4 min-h-0 scroll-smooth relative z-10"
      >
        {messages.length === 0 && !isTyping ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center justify-center h-full"
          >
            <div className="text-center space-y-4">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", stiffness: 180, delay: 0.1 }}
                className="w-16 h-16 mx-auto rounded-2xl bg-gradient-to-br from-indigo-500/15 to-violet-500/10 border border-indigo-500/15 flex items-center justify-center shadow-[0_0_32px_rgba(99,102,241,0.06)]"
              >
                <Sparkles className="w-7 h-7 text-indigo-400/50" />
              </motion.div>
              <motion.p
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                className="text-white/15 text-sm"
              >
                AI 助手正在准备...
              </motion.p>
            </div>
          </motion.div>
        ) : (
          <ChatMessages messages={messages} isTyping={isTyping} />
        )}
      </div>

      {/* ====== 输入框区域 ====== */}
      <div className="flex-shrink-0 pb-6 relative z-10">
        {/* 生成画像按钮：有用户消息且未出画像时显示 */}
        {!portrait && messages.some((m) => m.role === "user") && (
          <div className="flex justify-center mb-3">
            <motion.button
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={handleGeneratePortrait}
              disabled={isTyping || uploading}
              whileHover={{ scale: 1.03 }}
              whileTap={{ scale: 0.97 }}
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-gradient-to-r from-indigo-500/20 to-violet-500/20 backdrop-blur-md border border-indigo-400/30 text-indigo-200/90 text-sm font-medium hover:from-indigo-500/30 hover:to-violet-500/30 hover:border-indigo-400/50 hover:text-indigo-100 transition-all disabled:opacity-40 disabled:cursor-not-allowed shadow-[0_0_24px_rgba(99,102,241,0.12)]"
            >
              <Sparkles className="w-4 h-4" />
              生成雷达图
            </motion.button>
          </div>
        )}
        <ChatInput
          onSend={handleSend}
          onFileSelect={handleFileSelect}
          disabled={isTyping || stage === "analysis"}
          uploading={uploading}
        />

        {/* 底部操作按钮 */}
        <AnimatePresence>
          {portrait && (
            <motion.div
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 8 }}
              className="flex items-center justify-center gap-4 mt-4"
            >
              <motion.button
                onClick={handleReset}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-white/[0.03] backdrop-blur-md border border-white/[0.08] text-white/30 text-sm hover:bg-white/[0.06] hover:text-white/50 hover:border-white/[0.15] transition-all"
              >
                <RotateCcw className="w-3.5 h-3.5" /> 重新评估
              </motion.button>
              <motion.button
                onClick={() => navigate("/dashboard/direction")}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="inline-flex items-center gap-2 px-6 py-2.5 rounded-full bg-white text-[#030303] font-semibold text-sm hover:bg-white/90 shadow-lg shadow-white/10 transition-all"
              >
                下一步：方向选择 <ArrowRight className="w-4 h-4" />
              </motion.button>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}

function _labelScore(label: string): number {
  return (
    { "优秀": 85, "突出": 90, "强": 85, "较强": 80, "良好": 70, "中等": 50, "一般": 35, "较弱": 20 }[label] || 50
  );
}
