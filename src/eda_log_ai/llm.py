from __future__ import annotations

import json
import urllib.error
import urllib.request

from eda_log_ai.config import get_setting
from eda_log_ai.models import AnalysisResult
from eda_log_ai.render import _normalize


DEFAULT_QWEN_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
DEFAULT_QWEN_MODEL = "qwen3-max"


def llm_available() -> bool:
    return bool(_api_key())


def enhance_with_qwen(result: AnalysisResult, *, model: str = DEFAULT_QWEN_MODEL) -> str:
    key = _api_key()
    if not key:
        return "LLM enhancement skipped: no API key found in environment or .env."

    payload = {
        "model": model or default_model(),
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是一个 EDA 日志分析助手。只能基于用户提供的结构化 parser 输出回答，"
                    "不要编造日志中没有的事实。请用中文输出，并且只返回一个 JSON 对象，不要使用 Markdown。"
                    "JSON 必须包含这些字段："
                    "summary: 一句话中文摘要；"
                    "confirmed_facts: 字符串数组，列出已经由 parser/case 库确认的事实，最多 4 条；"
                    "root_cause_hypothesis: 字符串数组，列出可能根因，最多 3 条；"
                    "next_steps: 字符串数组，列出下一步排查动作，最多 5 条；"
                    "escalation: 一句话说明应该升级给谁；"
                    "caveat: 一句话说明这是辅助 triage，修改工程文件前需要人工确认。"
                ),
            },
            {
                "role": "user",
                "content": json.dumps(_normalize(result), ensure_ascii=False),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 700,
        "response_format": {"type": "json_object"},
    }
    request = urllib.request.Request(
        f"{_base_url().rstrip('/')}/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        return f"LLM enhancement failed: {exc}"

    choices = body.get("choices", [])
    if not choices:
        return "LLM enhancement returned no choices."
    message = choices[0].get("message", {})
    return _pretty_json_or_text(str(message.get("content") or "LLM enhancement returned an empty message."))


def _api_key() -> str:
    return get_setting("DASHSCOPE_API_KEY") or get_setting("QWEN_API_KEY") or get_setting("OPENAI_API_KEY")


def default_model() -> str:
    return get_setting("QWEN_MODEL", DEFAULT_QWEN_MODEL)


def _base_url() -> str:
    return get_setting("QWEN_BASE_URL", DEFAULT_QWEN_BASE_URL)


def _pretty_json_or_text(value: str) -> str:
    text = value.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
    try:
        return json.dumps(json.loads(text), ensure_ascii=False, indent=2)
    except json.JSONDecodeError:
        return value
