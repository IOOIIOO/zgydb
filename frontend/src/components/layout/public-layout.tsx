import { Link, Outlet } from "react-router-dom";

/**
 * 公开页布局
 * 用于首页、快速了解、登录、注册等无需认证的页面
 */
export function PublicLayout() {
  return (
    <div className="min-h-screen bg-[#030303]">
      {/* 顶部导航 */}
      <header className="absolute top-0 left-0 right-0 z-20">
        <div className="container mx-auto px-4 md:px-6 flex items-center justify-between h-16">
          <Link
            to="/"
            className="text-white/80 font-semibold text-lg hover:text-white transition-colors"
          >
            职途 · CareerPath
          </Link>
          <nav className="flex items-center gap-6">
            <Link
              to="/quick-overview"
              className="text-white/50 text-sm hover:text-white/80 transition-colors"
            >
              快速了解
            </Link>
            <Link
              to="/login"
              className="text-white/50 text-sm hover:text-white/80 transition-colors"
            >
              登录
            </Link>
            <Link
              to="/register"
              className="px-4 py-1.5 rounded-full bg-white/[0.06] border border-white/[0.12] text-white/70 text-sm hover:bg-white/[0.12] transition-all"
            >
              注册
            </Link>
          </nav>
        </div>
      </header>

      {/* 页面内容 */}
      <main>
        <Outlet />
      </main>
    </div>
  );
}
