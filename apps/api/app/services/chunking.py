from dataclasses import dataclass
import re

DEFAULT_CHUNK_SIZE = 1400
DEFAULT_CHUNK_OVERLAP = 150
MAX_SECTION_CHARS = 1500


@dataclass(frozen=True)
class TextChunk:
    content: str
    heading_path: list[str]


def split_text(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE, overlap: int = DEFAULT_CHUNK_OVERLAP) -> list[str]:
    return [chunk.content for chunk in split_markdown_text(text, chunk_size, overlap)]


def split_markdown_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[TextChunk]:
    normalized = "\n".join(line.rstrip() for line in text.splitlines()).strip()
    if not normalized:
        return []

    chunks: list[TextChunk] = []
    for section in _split_markdown_sections(normalized):
        if len(section.content) <= MAX_SECTION_CHARS:
            chunks.append(section)
            continue

        for child in _split_long_section(section, chunk_size, overlap):
            chunks.append(child)

    return chunks


def estimate_token_count(text: str) -> int:
    return max(1, len(text) // 4)


def heading_to_string(heading_path: list[str]) -> str:
    return " > ".join(heading_path)


def _split_markdown_sections(text: str) -> list[TextChunk]:
    heading_pattern = re.compile(r"^(#{1,3})\s+(.+?)\s*$")
    heading_path: list[str] = []
    current_lines: list[str] = []
    current_path: list[str] = []
    sections: list[TextChunk] = []

    def flush() -> None:
        content = "\n".join(current_lines).strip()
        has_body = any(line.strip() and not heading_pattern.match(line) for line in current_lines)
        if content and has_body:
            sections.append(TextChunk(content=content, heading_path=current_path.copy()))

    for line in text.splitlines():
        match = heading_pattern.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            flush()
            current_lines = []
            if len(heading_path) < level:
                heading_path.extend([""] * (level - len(heading_path)))
            heading_path[level - 1] = title
            del heading_path[level:]
            current_path = [item for item in heading_path if item]
            current_lines.append(line)
            continue
        current_lines.append(line)

    flush()
    return sections


def _split_long_section(section: TextChunk, chunk_size: int, overlap: int) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    start = 0
    text_length = len(section.content)

    while start < text_length:
        end = _find_split_end(section.content, start, min(start + chunk_size, text_length))
        chunk = section.content[start:end].strip()
        if chunk:
            chunks.append(TextChunk(content=chunk, heading_path=section.heading_path))
        if end == text_length:
            break
        start = max(end - overlap, start + 1)

    return chunks


def _find_split_end(text: str, start: int, proposed_end: int) -> int:
    if proposed_end >= len(text):
        return len(text)

    window = text[start:proposed_end]
    candidates = [window.rfind(marker) for marker in ("\n\n", "。", ". ", "\n")]
    best = max(candidates)
    if best < 400:
        return proposed_end
    return start + best + 1
