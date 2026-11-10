import argparse
import sys

from sovereign_ai.chunking import chunk_markdown_file, iter_markdown_paths
from sovereign_ai.chroma_store import ChromaStore
from sovereign_ai.config_loaders import load_models_config, load_rag_config
from sovereign_ai.ollama_client import OllamaClient
from sovereign_ai.paths import repo_root


def run_ingest(*, reset: bool = False) -> int:
    root = repo_root()
    rag = load_rag_config(root)
    models = load_models_config(root)
    chunk_size = int(rag.get("chunk_size", 512))
    chunk_overlap = int(rag.get("chunk_overlap", 64))
    collection = str(rag.get("collection", "default"))
    raw_dir = root / "data" / "raw"
    paths = iter_markdown_paths(raw_dir)
    if not paths:
        print(f"No .md files under {raw_dir}", file=sys.stderr)
        return 1

    all_chunks = []
    for p in paths:
        all_chunks.extend(chunk_markdown_file(p, root, chunk_size, chunk_overlap))
    if not all_chunks:
        print("No chunks produced.", file=sys.stderr)
        return 1

    store = ChromaStore(root / "storage" / "chroma", collection)
    if reset:
        store.reset()

    client = OllamaClient(
        str(models["ollama_base_url"]),
        str(models["chat_model"]),
        str(models["embed_model"]),
    )

    batch_size = 8
    for i in range(0, len(all_chunks), batch_size):
        batch = all_chunks[i : i + batch_size]
        embeddings = [client.embed(c.text) for c in batch]
        store.upsert_chunks(batch, embeddings)
        print(f"Indexed {min(i + batch_size, len(all_chunks))}/{len(all_chunks)} chunks")

    print(f"Done. Collection={collection!r}, chunks={len(all_chunks)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Ingest data/raw markdown into Chroma")
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Clear the Chroma collection before ingest",
    )
    args = parser.parse_args(argv)
    return run_ingest(reset=args.reset)
