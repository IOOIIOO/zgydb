import client from "./client";
import type { LoginRequest, LoginResponse, RegisterRequest } from "../types";

/** 用户注册 */
export function register(data: RegisterRequest): Promise<LoginResponse> {
  return client.post("/auth/register", data);
}

/** 用户登录 */
export function login(data: LoginRequest): Promise<LoginResponse> {
  return client.post("/auth/login", data);
}

/** 获取当前用户信息 */
export function getCurrentUser(): Promise<LoginResponse["user"]> {
  return client.get("/auth/me");
}
