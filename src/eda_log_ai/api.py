from __future__ import annotations

from pathlib import Path

from eda_log_ai.analyzer import analyze_log
from eda_log_ai.config import PROJECT_ROOT
from eda_log_ai.llm import DEFAULT_QWEN_MODEL, default_model, enhance_with_qwen, llm_available
from eda_log_ai.render import _normalize

try:
    from fastapi import FastAPI
    from fastapi.staticfiles import StaticFiles
    from pydantic import BaseModel
except ImportError as exc:  # pragma: no cover
    raise RuntimeError("Install optional API dependencies with: pip install -e .[api]") from exc


class AnalyzeRequest(BaseModel):
    log_text: str
    use_llm: bool = False
    model: str = DEFAULT_QWEN_MODEL


app = FastAPI(title="EDA Log AI", version="0.1.0")
FRONTEND_DIR = PROJECT_ROOT / "frontend"


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/config")
def config() -> dict[str, object]:
    return {
        "llm_available": llm_available(),
        "default_model": default_model(),
        "frontend_available": FRONTEND_DIR.exists(),
    }


@app.post("/analyze")
def analyze(request: AnalyzeRequest):
    result = analyze_log(request.log_text)
    payload = _normalize(result)
    if request.use_llm:
        payload["llm_note"] = enhance_with_qwen(result, model=request.model)
    return payload


if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=Path(FRONTEND_DIR), html=True), name="frontend")
