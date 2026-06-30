"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Bot, User, Sparkles } from "lucide-react";
import { cn } from "@/lib/utils";

export interface ChatMessage {
  id: string;
  role: "user" | "ai";
  content: string;
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
          className="w-2 h-2 bg-white/80 rounded-full"
          initial={{ opacity: 0.2 }}
          animate={{
            opacity: [0.2, 0.9, 0.2],
            scale: [0.8, 1.15, 0.8],
          }}
          transition={{
            duration: 1.2,
            repeat: Infinity,
            delay: dot * 0.15,
            ease: "easeInOut",
          }}
          style={{
            boxShadow: "0 0 6px rgba(255,255,255,0.25)",
          }}
        />
      ))}
    </div>
  );
}

export function ChatMessages({ messages, isTyping }: ChatMessagesProps) {
  return (
    <div className="flex flex-col gap-5 pb-2">
      <AnimatePresence>
        {messages.map((msg, i) => {
          const isFirst = i === 0;
          return (
            <motion.div
              key={msg.id}
              initial={isFirst ? { opacity: 0, y: 20, scale: 0.96 } : { opacity: 0, y: 12, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              transition={
                isFirst
                  ? { duration: 0.5, ease: "easeOut" }
                  : { duration: 0.25, ease: "easeOut" }
              }
              className={cn(
                "flex gap-3",
                msg.role === "user" ? "justify-end" : "justify-start"
              )}
            >
              {/* AI 头像 */}
              {msg.role === "ai" && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
                  className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500/15 to-violet-500/10 border border-indigo-500/20 flex items-center justify-center mt-0.5 shadow-[0_0_12px_rgba(99,102,241,0.08)]"
                >
                  <Sparkles className="w-4 h-4 text-indigo-400/70" />
                </motion.div>
              )}

              {/* 消息气泡 */}
              <motion.div
                layout
                className={cn(
                  "max-w-[75%] rounded-2xl px-5 py-3.5 text-sm leading-relaxed",
                  msg.role === "ai"
                    ? "bg-white/[0.025] backdrop-blur-xl border border-white/[0.06] text-white/70 rounded-tl-md shadow-[0_2px_16px_rgba(0,0,0,0.15)]"
                    : "bg-gradient-to-br from-indigo-500/[0.15] to-violet-500/[0.10] border border-indigo-500/20 text-white/85 rounded-tr-md shadow-[0_2px_16px_rgba(99,102,241,0.06)]"
                )}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </motion.div>

              {/* 用户头像 */}
              {msg.role === "user" && (
                <motion.div
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: "spring", stiffness: 200 }}
                  className="flex-shrink-0 w-9 h-9 rounded-full bg-white/[0.04] border border-white/[0.08] flex items-center justify-center mt-0.5"
                >
                  <User className="w-4 h-4 text-white/45" />
                </motion.div>
              )}
            </motion.div>
          );
        })}
      </AnimatePresence>

      {/* AI 正在输入 */}
      <AnimatePresence>
        {isTyping && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 10 }}
            className="flex gap-3"
          >
            <div className="flex-shrink-0 w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500/15 to-violet-500/10 border border-indigo-500/20 flex items-center justify-center mt-0.5 shadow-[0_0_12px_rgba(99,102,241,0.08)]">
              <Sparkles className="w-4 h-4 text-indigo-400/70" />
            </div>
            <div className="bg-white/[0.025] backdrop-blur-xl border border-white/[0.06] rounded-2xl rounded-tl-md shadow-[0_2px_16px_rgba(0,0,0,0.15)]">
              <TypingDots />
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
