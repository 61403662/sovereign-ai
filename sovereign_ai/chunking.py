from dataclasses import dataclass
from pathlib import Path
import hashlib
import re

# Leading YAML block used by Cursor/.plan.md etc.; not a Markdown heading.
_YAML_FRONTMATTER_RE = re.compile(r"\A---\r?\n.*?\r?\n---\r?\n", re.DOTALL)


def strip_yaml_frontmatter(text: str) -> str:
    """Remove a leading --- ... --- block so todos/metadata are not indexed."""
    return _YAML_FRONTMATTER_RE.sub("", text, count=1)


@dataclass(frozen=True)
class TextChunk:
    chunk_id: str
    text: str
    source: str
    heading: str


def split_markdown_sections(text: str) -> list[tuple[str, str]]:
    """Split by markdown headings; returns (heading, body) pairs."""
    parts: list[tuple[str, str]] = []
    current_heading = ""
    buf: list[str] = []

    for line in text.splitlines():
        m = re.match(r"^(#{1,6})\s+(.+)$", line)
        if m:
            if buf or current_heading:
                parts.append((current_heading, "\n".join(buf).strip()))
            current_heading = m.group(2).strip()
            buf = []
        else:
            buf.append(line)
    if buf or current_heading:
        parts.append((current_heading, "\n".join(buf).strip()))
    if not parts and text.strip():
        parts.append(("", text.strip()))
    return [(h, b) for h, b in parts if b]


def document_title(text: str) -> str:
    for line in text.splitlines():
        m = re.match(r"^#\s+(.+)$", line)
        if m:
            return m.group(1).strip()
    return ""


def chunk_text_for_index(doc_title: str, heading: str, piece: str) -> str:
    """Prefix section (and doc title) so embeddings match natural questions."""
    section = heading or ""
    if section and doc_title and section != doc_title:
        prefix = f"{doc_title} > {section}"
    elif section:
        prefix = section
    elif doc_title:
        prefix = doc_title
    else:
        return piece
    return f"{prefix}\n\n{piece}"


def sliding_chunks(body: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    if len(body) <= chunk_size:
        return [body] if body else []
    chunks: list[str] = []
    start = 0
    while start < len(body):
        end = start + chunk_size
        chunks.append(body[start:end])
        if end >= len(body):
            break
        start = max(0, end - chunk_overlap)
    return chunks


def chunk_markdown_file(
    path: Path,
    root: Path,
    chunk_size: int,
    chunk_overlap: int,
) -> list[TextChunk]:
    text = strip_yaml_frontmatter(path.read_text(encoding="utf-8"))
    title = document_title(text)
    rel = path.relative_to(root).as_posix()
    out: list[TextChunk] = []
    for heading, body in split_markdown_sections(text):
        for piece in sliding_chunks(body, chunk_size, chunk_overlap):
            indexed = chunk_text_for_index(title, heading, piece)
            digest = hashlib.sha256(f"{rel}:{heading}:{piece}".encode()).hexdigest()[:16]
            chunk_id = f"{rel}#{digest}"
            out.append(
                TextChunk(
                    chunk_id=chunk_id,
                    text=indexed,
                    source=rel,
                    heading=heading or "(无标题)",
                )
            )
    return out


def iter_markdown_paths(raw_dir: Path) -> list[Path]:
    if not raw_dir.is_dir():
        return []
    return sorted(raw_dir.rglob("*.md"))
