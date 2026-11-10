import argparse
import sys

from sovereign_ai.chroma_store import ChromaStore
from sovereign_ai.config_loaders import load_models_config, load_rag_config
from sovereign_ai.ollama_client import OllamaClient
from sovereign_ai.paths import repo_root

SYSTEM_PROMPT = (
    "你是本地文档助手。仅根据用户提供的「检索上下文」回答问题。"
    "若上下文不足以回答，请明确说「上下文未包含相关信息」，不要编造。"
    "回答使用简体中文，条理清晰。"
)


def format_context(hits: list[dict]) -> str:
    blocks = []
    for i, h in enumerate(hits, start=1):
        src = h.get("source") or ""
        heading = h.get("heading") or ""
        text = h.get("text") or ""
        blocks.append(f"[{i}] 来源: {src}#{heading}\n{text}")
    return "\n\n".join(blocks)


def format_citations(hits: list[dict]) -> str:
    lines = ["", "---", "引用来源:"]
    seen: set[tuple[str, str]] = set()
    for h in hits:
        src = str(h.get("source") or "")
        heading = str(h.get("heading") or "")
        key = (src, heading)
        if key in seen:
            continue
        seen.add(key)
        lines.append(f"- [来源: {src}#{heading}]")
    return "\n".join(lines)


def run_ask(question: str) -> int:
    root = repo_root()
    rag = load_rag_config(root)
    models = load_models_config(root)
    top_k = int(rag.get("top_k", 5))
    collection = str(rag.get("collection", "default"))

    store = ChromaStore(root / "storage" / "chroma", collection)
    client = OllamaClient(
        str(models["ollama_base_url"]),
        str(models["chat_model"]),
        str(models["embed_model"]),
    )

    q_emb = client.embed(question)
    hits = store.query(q_emb, top_k)
    if not hits:
        print("向量库为空或无可命中段落，请先运行: python -m sovereign_ai.ingest", file=sys.stderr)
        return 1

    context = format_context(hits)
    user_content = f"检索上下文:\n\n{context}\n\n问题: {question}"

    answer = client.chat(
        [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ]
    )
    print(answer)
    print(format_citations(hits))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask a question using local RAG")
    parser.add_argument("question", nargs="?", help="Question text")
    args = parser.parse_args(argv)
    if not args.question:
        parser.error("question is required")
    return run_ask(args.question)
