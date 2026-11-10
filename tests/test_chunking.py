from pathlib import Path

from sovereign_ai.chunking import chunk_markdown_file, sliding_chunks, split_markdown_sections


def test_split_markdown_sections():
    text = "# Title\n\nintro\n\n## Section A\n\nbody a\n\n## Section B\n\nbody b"
    parts = split_markdown_sections(text)
    assert len(parts) >= 2
    headings = [h for h, _ in parts]
    assert "Section A" in headings


def test_sliding_chunks_overlap():
    body = "a" * 100
    chunks = sliding_chunks(body, chunk_size=40, chunk_overlap=10)
    assert len(chunks) > 1
    assert all(len(c) <= 40 for c in chunks)


def test_chunk_markdown_file(tmp_path: Path):
    root = tmp_path
    raw = root / "data" / "raw"
    raw.mkdir(parents=True)
    md = raw / "note.md"
    md.write_text("## 检验\n\n耐压 500 V DC。\n", encoding="utf-8")
    chunks = chunk_markdown_file(md, root, chunk_size=512, chunk_overlap=64)
    assert len(chunks) == 1
    assert "500" in chunks[0].text
    assert chunks[0].source == "data/raw/note.md"
