from typing import Any

import httpx


class OllamaClient:
    def __init__(self, base_url: str, chat_model: str, embed_model: str, timeout: float = 120.0):
        self.base_url = base_url.rstrip("/")
        self.chat_model = chat_model
        self.embed_model = embed_model
        self.timeout = timeout

    def embed(self, text: str) -> list[float]:
        with httpx.Client(timeout=self.timeout) as client:
            data = self._embed_request(client, text)
        emb = data.get("embedding")
        if emb is None and "embeddings" in data:
            emb = data["embeddings"][0] if data["embeddings"] else None
        if not isinstance(emb, list):
            raise RuntimeError(f"Unexpected embeddings response: {data!r}")
        return [float(x) for x in emb]

    def _embed_request(self, client: httpx.Client, text: str) -> dict[str, Any]:
        attempts = (
            ("POST", "/api/embeddings", {"model": self.embed_model, "prompt": text}),
            ("POST", "/api/embed", {"model": self.embed_model, "input": text}),
        )
        last_err: Exception | None = None
        for _method, path, payload in attempts:
            try:
                r = client.post(f"{self.base_url}{path}", json=payload)
                r.raise_for_status()
                return r.json()
            except Exception as e:  # noqa: BLE001 — try next Ollama API shape
                last_err = e
        raise RuntimeError(f"All embed endpoints failed: {last_err}")

    def chat(self, messages: list[dict[str, str]], stream: bool = False) -> str:
        payload: dict[str, Any] = {
            "model": self.chat_model,
            "messages": messages,
            "stream": stream,
        }
        with httpx.Client(timeout=self.timeout) as client:
            r = client.post(f"{self.base_url}/api/chat", json=payload)
            r.raise_for_status()
            data = r.json()
        msg = data.get("message") or {}
        content = msg.get("content")
        if not isinstance(content, str):
            raise RuntimeError(f"Unexpected chat response: {data!r}")
        return content
