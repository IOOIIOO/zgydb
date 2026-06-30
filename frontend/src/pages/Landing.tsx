import { Link } from "react-router-dom";
import { HeroGeometric } from "../components/ui/shape-landing-hero";
import { ArrowRight, Compass } from "lucide-react";

/**
 * 首页 Landing
 * 品牌展示 + 快速了解入口 + 开始测评 CTA
 */
export default function Landing() {
  return (
    <div className="relative">
      <HeroGeometric />

      {/* CTA 按钮区 */}
      <div className="absolute bottom-12 left-0 right-0 z-10 flex flex-col sm:flex-row items-center justify-center gap-4 px-4">
        <Link
          to="/register"
          className="inline-flex items-center gap-2 px-8 py-3 rounded-full bg-white text-[#030303] font-semibold text-base hover:bg-white/90 transition-all shadow-[0_0_40px_rgba(255,255,255,0.15)]"
        >
          开始测评
          <ArrowRight className="w-4 h-4" />
        </Link>
        <Link
          to="/quick-overview"
          className="inline-flex items-center gap-2 px-8 py-3 rounded-full bg-white/[0.04] border border-white/[0.12] text-white/70 font-medium text-base hover:bg-white/[0.08] transition-all"
        >
          快速了解
          <Compass className="w-4 h-4" />
        </Link>
      </div>
    </div>
  );
}
