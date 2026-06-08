from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader

SUPPORTED_FILE_TYPES = {".pdf", ".txt", ".md", ".markdown"}


def infer_file_type(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_FILE_TYPES:
        raise ValueError("Unsupported file type. Upload PDF, TXT, or Markdown files.")
    return "markdown" if suffix in {".md", ".markdown"} else suffix.lstrip(".")


async def extract_text_from_upload(file: UploadFile) -> str:
    file_type = infer_file_type(file.filename or "")
    content = await file.read()

    if file_type == "pdf":
        return extract_pdf_text(content)

    return decode_text(content)


def decode_text(content: bytes) -> str:
    for encoding in ("utf-8", "utf-8-sig", "gb18030", "latin-1"):
        try:
            return content.decode(encoding)
        except UnicodeDecodeError:
            continue
    return content.decode("utf-8", errors="ignore")


def extract_pdf_text(content: bytes) -> str:
    from io import BytesIO

    reader = PdfReader(BytesIO(content))
    pages = []
    for index, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"[Page {index}]\n{text.strip()}")
    return "\n\n".join(pages)

