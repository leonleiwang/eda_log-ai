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
                    "You are an EDA log triage assistant. Summarize only from structured parser output. "
                    "Separate confirmed facts from hypotheses. Keep the answer concise and practical."
                ),
            },
            {
                "role": "user",
                "content": json.dumps(_normalize(result), ensure_ascii=False),
            },
        ],
        "temperature": 0.2,
        "max_tokens": 700,
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
    return str(message.get("content") or "LLM enhancement returned an empty message.")


def _api_key() -> str:
    return get_setting("DASHSCOPE_API_KEY") or get_setting("QWEN_API_KEY") or get_setting("OPENAI_API_KEY")


def default_model() -> str:
    return get_setting("QWEN_MODEL", DEFAULT_QWEN_MODEL)


def _base_url() -> str:
    return get_setting("QWEN_BASE_URL", DEFAULT_QWEN_BASE_URL)
