import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { login } from "../../api/auth";
import { LogIn, Mail, Lock } from "lucide-react";

export default function Login() {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault(); setError("");
    if (!email || !password) { setError("请填写邮箱和密码"); return; }
    setLoading(true);
    try {
      const res = await login({ email, password });
      localStorage.setItem("access_token", res.access_token);
      navigate("/dashboard", { replace: true });
    } catch (err: any) {
      setError(err?.response?.data?.detail || err?.message || "登录失败");
    } finally { setLoading(false); }
  };

  return (
    <div className="min-h-screen bg-[#030303] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.23, 0.86, 0.39, 0.96] }}
        className="w-full max-w-xl px-4"
      >
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold">
            <span className="bg-clip-text text-transparent bg-gradient-to-b from-white to-white/80">
              欢迎回来
            </span>
          </h1>
          <p className="text-white/30 text-sm mt-2">登录你的账户继续职业规划</p>
        </div>

        <form onSubmit={handleSubmit} className="p-8 rounded-2xl bg-white/[0.02] border border-white/[0.06] space-y-5">
          {error && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }}
              className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/20 text-rose-400/90 text-sm">
              {error}
            </motion.div>
          )}

          <div className="relative">
            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/15" />
            <input
              type="email" placeholder="邮箱地址" value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder:text-white/15 outline-none focus:border-white/25 focus:bg-white/[0.06] transition-all"
            />
          </div>

          <div className="relative">
            <Lock className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-white/15" />
            <input
              type="password" placeholder="密码" value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full pl-11 pr-4 py-3 rounded-xl bg-white/[0.04] border border-white/[0.08] text-white placeholder:text-white/15 outline-none focus:border-white/25 focus:bg-white/[0.06] transition-all"
            />
          </div>

          <button
            type="submit" disabled={loading}
            className="w-full py-3 rounded-xl bg-white text-[#030303] font-semibold hover:bg-white/90 transition-all disabled:opacity-40 flex items-center justify-center gap-2"
          >
            <LogIn className="w-4 h-4" />
            {loading ? "登录中..." : "登录"}
          </button>

          <p className="text-white/25 text-sm text-center">
            还没有账号？{" "}
            <Link to="/register" className="text-white/50 hover:text-white/80 transition-colors">创建账户</Link>
          </p>
        </form>
      </motion.div>
    </div>
  );
}
