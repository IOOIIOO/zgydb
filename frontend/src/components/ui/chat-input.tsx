"use client";

import { useRef, useCallback, useEffect, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Upload, Loader2, X } from "lucide-react";
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
  const [inputFocused, setInputFocused] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [attachments, setAttachments] = useState<{ name: string; file: File }[]>([]);
  const { textareaRef, adjustHeight } = useAutoResizeTextarea(60, 200);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 鼠标追踪
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
    };
    window.addEventListener("mousemove", handleMouseMove);
    return () => window.removeEventListener("mousemove", handleMouseMove);
  }, []);

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
      setAttachments((prev) => [...prev, { name: file.name, file }]);
      onFileSelect(file);
      e.target.value = "";
    }
  };

  const removeAttachment = (index: number) => {
    setAttachments((prev) => prev.filter((_, i) => i !== index));
  };

  return (
    <>
      {/* 鼠标跟随光晕 — 仅聚焦时显示 */}
      {inputFocused && (
        <motion.div
          className="fixed w-[50rem] h-[50rem] rounded-full pointer-events-none z-0 opacity-[0.025] bg-gradient-to-r from-violet-500 via-fuchsia-500 to-indigo-500 blur-[96px]"
          animate={{
            x: mousePosition.x - 400,
            y: mousePosition.y - 400,
          }}
          transition={{
            type: "spring",
            damping: 25,
            stiffness: 120,
            mass: 0.5,
          }}
        />
      )}

      <motion.div
        className="relative backdrop-blur-2xl bg-white/[0.02] rounded-2xl border border-white/[0.05] shadow-2xl"
        initial={{ scale: 0.98 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1 }}
      >
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
            onFocus={() => setInputFocused(true)}
            onBlur={() => setInputFocused(false)}
            placeholder="输入你的回答... (Enter 发送，Shift+Enter 换行)"
            disabled={disabled}
            className={cn(
              "w-full px-4 py-3",
              "resize-none",
              "bg-transparent",
              "border-none",
              "text-white/85 text-sm",
              "focus:outline-none",
              "placeholder:text-white/15",
              "min-h-[60px]"
            )}
            style={{ overflow: "hidden" }}
          />
        </div>

        {/* 附件标签 */}
        <AnimatePresence>
          {attachments.length > 0 && (
            <motion.div
              className="px-4 pb-3 flex gap-2 flex-wrap"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
            >
              {attachments.map((f, index) => (
                <motion.div
                  key={index}
                  className="flex items-center gap-2 text-xs bg-white/[0.04] backdrop-blur-md py-1.5 px-3 rounded-lg text-white/70 border border-white/[0.06]"
                  initial={{ opacity: 0, scale: 0.9 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                >
                  <span>{f.name}</span>
                  <button
                    onClick={() => removeAttachment(index)}
                    className="text-white/40 hover:text-white transition-colors"
                  >
                    <X className="w-3 h-3" />
                  </button>
                </motion.div>
              ))}
            </motion.div>
          )}
        </AnimatePresence>

        {/* 工具栏 */}
        <div className="px-4 pb-4 flex items-center justify-between gap-4">
          <div className="flex items-center gap-1.5">
            {/* 上传按钮 */}
            <motion.button
              type="button"
              onClick={() => fileInputRef.current?.click()}
              whileTap={{ scale: 0.93 }}
              whileHover={{ scale: 1.05 }}
              disabled={disabled || uploading}
              className="p-2.5 text-white/35 hover:text-white/85 rounded-xl transition-colors relative group disabled:opacity-30"
              title="上传简历文件 (PDF/图片)"
            >
              {uploading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <Upload className="w-4 h-4" />
              )}
              <motion.span
                className="absolute inset-0 bg-white/[0.06] rounded-xl opacity-0 group-hover:opacity-100 transition-opacity"
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
            whileHover={value.trim() && !disabled ? { scale: 1.02 } : {}}
            whileTap={value.trim() && !disabled ? { scale: 0.97 } : {}}
            disabled={disabled || !value.trim()}
            className={cn(
              "px-5 py-2.5 rounded-xl text-sm font-medium transition-all flex items-center gap-2",
              value.trim() && !disabled
                ? "bg-white text-[#0A0A0B] shadow-lg shadow-white/8"
                : "bg-white/[0.04] text-white/25 cursor-not-allowed"
            )}
          >
            <Send className="w-3.5 h-3.5" />
            <span>发送</span>
          </motion.button>
        </div>
      </motion.div>
    </>
  );
}
