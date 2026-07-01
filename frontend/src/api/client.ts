import axios from "axios";

/**
 * Axios 实例封装
 * - 自动注入 Token
 * - 统一 baseURL
 * - 响应拦截处理错误
 */
const client = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  timeout: 180000,
  headers: {
    "Content-Type": "application/json",
  },
});

// 请求拦截：注入 Token
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("access_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// 响应拦截：统一错误处理
client.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("access_token");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  },
);

export default client;
