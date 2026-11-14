from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from sovereign_ai.ask.runner import ask_question

_STATIC = Path(__file__).resolve().parent / "static"

app = FastAPI(title="sovereign-ai", version="0.1.0")


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=8000)


@app.get("/")
def index() -> FileResponse:
    return FileResponse(_STATIC / "index.html")


@app.post("/api/ask")
def api_ask(body: AskRequest) -> dict:
    result = ask_question(body.question)
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
        "answer": result["answer"],
        "citations": result["citations"],
    }


@app.get("/health")
def health() -> dict:
    return {"ok": True}