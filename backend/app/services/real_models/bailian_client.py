"""
阿里云百炼 OpenAI 兼容 API 客户端

端点: https://{workspace_id}.cn-beijing.maas.aliyuncs.com/compatible-mode/v1
模型: qwen3.7-plus (多模态 + 联网搜索)
"""

import json
import re
import requests
from app.config import settings


class BailianClient:
    """百炼 API 共享客户端 (单例，线程安全)"""

    def __init__(self):
        self.base_url = f"{settings.BAILIAN_BASE_URL}/chat/completions"
        self.model = settings.BAILIAN_MODEL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {settings.DASHSCOPE_API_KEY}",
            "Content-Type": "application/json",
        })

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024,
             response_format: dict | None = None) -> str:
        """通用对话，返回纯文本

        Args:
            response_format: 可选，如 {"type":"json_object"} 启用原生JSON模式，减少生成时间
        """
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if response_format:
            body["response_format"] = response_format
        try:
            r = self.session.post(self.base_url, json=body, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(f"Bailian API error {r.status_code}: {r.text[:300]}")
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, TypeError) as e:
            raise RuntimeError(f"Bailian API 连接失败: {e}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Bailian API 响应格式异常: {e}")

    def chat_json(self, messages: list[dict], temperature: float = 0.2, max_tokens: int = 1024) -> dict:
        """对话 + 从回复中提取 JSON（启用原生JSON模式，仅 1 次尝试）"""
        text = self.chat(messages, temperature=temperature, max_tokens=max_tokens,
                         response_format={"type": "json_object"})
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # 原生JSON模式失败时回退到括号计数提取
            json_str = self._extract_json(text)
            if json_str is None:
                raise ValueError(f"chat_json 无法提取JSON: {text[:300]}")
            try:
                return json.loads(json_str)
            except json.JSONDecodeError as e:
                raise ValueError(f"chat_json JSON解析失败: {e}, raw: {text[:300]}")

    @staticmethod
    def _extract_json(text: str) -> str | None:
        """用括号计数提取完整JSON（支持嵌套）"""
        start = text.find("{")
        if start == -1:
            return None
        depth = 0
        in_string = False
        escape = False
        for i in range(start, len(text)):
            ch = text[i]
            if escape:
                escape = False
                continue
            if ch == "\\":
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]
        return None

    def chat_with_search(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 1024) -> str:
        """联网搜索对话"""
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "enable_search": True,
        }
        try:
            r = self.session.post(self.base_url, json=body, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(f"Bailian search error {r.status_code}")
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, TypeError) as e:
            raise RuntimeError(f"Bailian 联网搜索连接失败: {e}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Bailian 联网搜索响应格式异常: {e}")


# 全局单例
_client = None


def get_client() -> BailianClient:
    global _client
    if _client is None:
        _client = BailianClient()
    return _client
