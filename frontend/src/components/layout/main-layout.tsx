import { Link, Navigate, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";
import { StepProgress } from "../ui/step-progress";
import { useProgress } from "../../hooks/useProgress";
import { LogOut, User } from "lucide-react";

/**
 * 主功能布局（需登录）
 * 包含导航栏、步骤进度条、内容区
 */
export function MainLayout() {
  const { user, loading, logout } = useAuth();
  const { progress } = useProgress();
  const navigate = useNavigate();

  // 登录守卫：加载完成后仍无用户 → 跳转登录
  if (!loading && !user) {
    return <Navigate to="/login" replace />;
  }

  const handleStepClick = (step: number) => {
    const routes: Record<number, string> = {
      1: "/dashboard/personality",
      2: "/dashboard/ability",
      3: "/dashboard/direction",
      4: "/dashboard/planning",
      5: "/dashboard/report",
    };
    navigate(routes[step]);
  };

  return (
    <div className="min-h-screen bg-[#030303]">
      {/* 顶部导航 */}
      <header className="sticky top-0 z-20 bg-[#030303]/80 backdrop-blur-md border-b border-white/[0.06]">
        <div className="container mx-auto px-4 md:px-6 flex items-center justify-between h-14">
          <Link
            to="/dashboard"
            className="text-white/80 font-semibold text-lg hover:text-white transition-colors"
          >
            职途 · CareerPath
          </Link>

          <nav className="flex items-center gap-4">
            <Link
              to="/reports"
              className="text-white/40 text-sm hover:text-white/70 transition-colors"
            >
              历史报告
            </Link>
            <div className="flex items-center gap-2 text-white/40">
              <User className="w-4 h-4" />
              <span className="text-sm">{user?.username ?? "用户"}</span>
            </div>
            <button
              type="button"
              onClick={logout}
              className="flex items-center gap-1 text-white/30 text-sm hover:text-white/60 transition-colors"
            >
              <LogOut className="w-3.5 h-3.5" />
              <span className="hidden sm:inline">退出</span>
            </button>
          </nav>
        </div>

        {/* 步骤进度条 */}
        {progress && (
          <div className="container mx-auto px-4">
            <StepProgress
              currentStep={progress.current_step}
              completedSteps={[
                progress.step1_completed,
                progress.step2_completed,
                progress.step3_completed,
                progress.step4_completed,
                progress.step5_completed,
              ]}
              onStepClick={handleStepClick}
            />
          </div>
        )}
      </header>

      {/* 页面内容 */}
      <main className="container mx-auto px-4 md:px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
