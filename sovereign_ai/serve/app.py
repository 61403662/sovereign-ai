from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from sovereign_ai.ask.runner import ask_question

_STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="sovereign-ai", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=8000)
    clarify_choice: str | None = Field(default=None, description="AI-13: rag | sql | compound")


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.post("/api/ask")
def api_ask(body: AskRequest) -> dict:
    try:
        result = ask_question(body.question, clarify_choice=body.clarify_choice)
    except Exception as e:  # noqa: BLE001 — surface to UI (local only)
        return {
            "ok": False,
            "error": f"服务端异常: {e!s}",
            "answer": "",
            "citations": [],
        }
    if result.get("clarify"):
        return {
            "ok": True,
            "clarify": True,
            "error": None,
            "route": "clarify",
            "question": result.get("question"),
            "prompt": result.get("prompt"),
            "options": result.get("options"),
            "hint": result.get("hint"),
            "answer": "",
            "citations": [],
        }
    if not result["ok"]:
        return {
            "ok": False,
            "error": result.get("error") or "ask failed",
            "answer": "",
            "citations": [],
        }
    return {
        "ok": True,
        "error": None,
        "route": result.get("route"),
        "routes": result.get("routes"),
        "intent": result.get("intent"),
        "data": result.get("data"),
        "answer": result["answer"],
        "citations": result["citations"],
        "citations_text": result.get("citations_text"),
    }


@app.get("/health")
def health() -> dict:
    from sovereign_ai.bom.db import database_ready
    from sovereign_ai.bom.nl_format import sql_nl_format_enabled

    return {
        "ok": True,
        "bom_db": database_ready(),
        "sql_nl_format": sql_nl_format_enabled(),
    }