import { useState, useEffect, useCallback } from "react";
import { getCurrentUser } from "../api/auth";
import type { User } from "../types";

/**
 * 认证状态 Hook
 * 管理用户登录状态、登录/登出操作
 */
export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  const checkAuth = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const u = await getCurrentUser();
      setUser(u);
    } catch {
      localStorage.removeItem("access_token");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    setUser(null);
    window.location.href = "/";
  }, []);

  return { user, loading, isLoggedIn: !!user, logout, refetch: checkAuth };
}
