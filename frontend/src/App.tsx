import { BrowserRouter, Routes, Route } from "react-router-dom";
import { PublicLayout } from "./components/layout/public-layout";
import { MainLayout } from "./components/layout/main-layout";

// 公开页面
import Landing from "./pages/Landing";
import DirectionList from "./pages/quick-overview/DirectionList";
import DirectionDetail from "./pages/quick-overview/DirectionDetail";
import Login from "./pages/auth/Login";
import Register from "./pages/auth/Register";

// 需登录页面
import Dashboard from "./pages/dashboard/Dashboard";
import Personality from "./pages/dashboard/Personality";
import Ability from "./pages/dashboard/Ability";
import DirectionSelect from "./pages/dashboard/DirectionSelect";
import Planning from "./pages/dashboard/Planning";
import Report from "./pages/dashboard/Report";
import ReportList from "./pages/reports/ReportList";
import ReportDetail from "./pages/reports/ReportDetail";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* 公开页布局 */}
        <Route element={<PublicLayout />}>
          <Route path="/" element={<Landing />} />
          <Route path="/quick-overview" element={<DirectionList />} />
          <Route path="/quick-overview/:directionId" element={<DirectionDetail />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
        </Route>

        {/* 需登录主布局 */}
        <Route element={<MainLayout />}>
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard/personality" element={<Personality />} />
          <Route path="/dashboard/ability" element={<Ability />} />
          <Route path="/dashboard/direction" element={<DirectionSelect />} />
          <Route path="/dashboard/planning" element={<Planning />} />
          <Route path="/dashboard/report" element={<Report />} />
          <Route path="/reports" element={<ReportList />} />
          <Route path="/reports/:reportId" element={<ReportDetail />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
