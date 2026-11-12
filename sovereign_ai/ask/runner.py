import argparse
import sys

from sovereign_ai.ask.citations import format_citations, select_citation_hits
from sovereign_ai.ask.rerank import (
    effective_top_k,
    merge_hits,
    missing_coop_ids,
    per_coop_fallback_queries,
    rerank_hits,
    supplemental_embed_queries,
    coop_ids_from_question,
)
from sovereign_ai.chroma_store import ChromaStore
from sovereign_ai.config_loaders import load_models_config, load_rag_config
from sovereign_ai.ollama_client import OllamaClient
from sovereign_ai.paths import repo_root

SYSTEM_PROMPT = (
    "你是本地文档助手。仅根据用户提供的「检索上下文」回答问题。"
    "若上下文不足以回答，请明确说「上下文未包含相关信息」，不要编造。"
    "用户会用日常中文提问，不会指定 Markdown 小节名；请综合所有检索段落作答。"
    "问开发、后端、接口、实现或计划时，优先采用技术实现相关段落（如 Backend Plan、API、routes），"
    "不要把范围/不做什么（Scope）或子计划导航索引当成完整计划。"
    "问 COOP 总体目标时，以「目标与原则」等开篇原则为准；上下文已有该节内容时直接概括，不要说「未直接提及」再推断。"
    "上下文若含 Backend Plan / Frontend Plan 等技术小节，以其为准作答；能列条就列条，保留 API 路径与字段名等原文标识。"
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


def run_ask(question: str) -> int:
    root = repo_root()
    rag = load_rag_config(root)
    models = load_models_config(root)
    base_top_k = int(rag.get("top_k", 5))
    cite_k = int(rag.get("cite_k", 1))
    cite_same_source = bool(rag.get("cite_same_source_as_top", True))
    collection = str(rag.get("collection", "default"))

    store = ChromaStore(root / "storage" / "chroma", collection)
    client = OllamaClient(
        str(models["ollama_base_url"]),
        str(models["chat_model"]),
        str(models["embed_model"]),
    )

    q_emb = client.embed(question)
    top_k = effective_top_k(question, base_top_k)
    primary = store.query(q_emb, top_k)
    extra_groups = [
        store.query(client.embed(sq), 4) for sq in supplemental_embed_queries(question)
    ]
    merged = merge_hits(primary, *extra_groups)
    for cid in missing_coop_ids(merged, _coop_ids(question)):
        for fq in per_coop_fallback_queries(cid):
            merged = merge_hits(merged, store.query(client.embed(fq), 4))
    hits = rerank_hits(question, merged)
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
    cite_hits = select_citation_hits(
        hits, cite_k=cite_k, same_source_as_top=cite_same_source
    )
    print(format_citations(cite_hits))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ask a question using local RAG")
    parser.add_argument("question", nargs="?", help="Question text")
    args = parser.parse_args(argv)
    if not args.question:
        parser.error("question is required")
    return run_ask(args.question)
