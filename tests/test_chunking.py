from pathlib import Path

from sovereign_ai.chunking import (
    chunk_markdown_file,
    chunk_text_for_index,
    sliding_chunks,
    split_markdown_sections,
    strip_yaml_frontmatter,
)


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


def test_chunk_text_for_index_includes_section_breadcrumb():
    body = "GET /dodItem/getBrotherFeature"
    indexed = chunk_text_for_index(
        "COOP-22162 Plan",
        "Backend Plan",
        body,
    )
    assert indexed.startswith("COOP-22162 Plan > Backend Plan")
    assert body in indexed


def test_strip_yaml_frontmatter():
    text = "---\nname: x\ntodos:\n  - id: a\n    content: short todo\n---\n\n## Backend Plan\n\nDetail here.\n"
    stripped = strip_yaml_frontmatter(text)
    assert "short todo" not in stripped
    assert "## Backend Plan" in stripped
    assert stripped.startswith("\n##") or stripped.startswith("##")


def test_chunk_markdown_skips_frontmatter_todos(tmp_path: Path):
    root = tmp_path
    raw = root / "data" / "raw"
    raw.mkdir(parents=True)
    md = raw / "plan.plan.md"
    md.write_text(
        "---\n"
        "todos:\n"
        "  - content: Add SKUNK branch in getBrotherFeature.\n"
        "---\n"
        "# Plan\n\n"
        "## Backend Plan\n\nGET /dodItem/getBrotherFeature SKUNK branch.\n",
        encoding="utf-8",
    )
    chunks = chunk_markdown_file(md, root, chunk_size=512, chunk_overlap=64)
    assert not any("todos:" in c.text for c in chunks)
    backend = [c for c in chunks if c.heading == "Backend Plan"]
    assert backend
    assert "Backend Plan" in backend[0].text
    assert "GET /dodItem" in backend[0].text


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
