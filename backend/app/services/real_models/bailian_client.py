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

    def chat(self, messages: list[dict], temperature: float = 0.7, max_tokens: int = 1024) -> str:
        """通用对话，返回纯文本"""
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            r = self.session.post(self.base_url, json=body, timeout=60)
            if r.status_code != 200:
                raise RuntimeError(f"Bailian API error {r.status_code}")
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, TypeError) as e:
            raise RuntimeError(f"Bailian API 连接失败: {e}")
        except (KeyError, IndexError) as e:
            raise RuntimeError(f"Bailian API 响应格式异常: {e}")

    def chat_json(self, messages: list[dict], temperature: float = 0.2) -> dict:
        """对话 + 从回复中提取 JSON（括号计数匹配嵌套，自动重试）"""
        msgs = list(messages)  # copy to avoid mutating caller's list
        for attempt in range(3):
            text = self.chat(msgs, temperature=temperature if attempt == 0 else 0.0)
            json_str = self._extract_json(text)
            if json_str is None:
                if attempt < 2:
                    msgs.append({"role": "user", "content": "请只返回JSON，不要任何解释。"})
                continue
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                if attempt < 2:
                    msgs.append({"role": "user", "content": "前一条JSON格式有误，请严格修复。"})
                continue
        raise ValueError(f"chat_json failed after 3 attempts: {text[:300]}")

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

    def chat_with_search(self, messages: list[dict], temperature: float = 0.3, max_tokens: int = 2048) -> str:
        """联网搜索对话"""
        body = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "enable_search": True,
        }
        try:
            r = self.session.post(self.base_url, json=body, timeout=120)
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
