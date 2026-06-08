from uuid import UUID

from fastapi import UploadFile
from pgvector.sqlalchemy import Vector
from sqlalchemy import Select, cast, func, select
from sqlalchemy.orm import Session

from app.models.document import Document, DocumentChunk, DocumentStatus
from app.models.workspace import Workspace
from app.services.chunking import estimate_token_count, split_text
from app.services.document_ingestion import extract_text_from_upload, infer_file_type
from app.services.embeddings import embed_text


async def ingest_document(db: Session, workspace: Workspace, file: UploadFile, title: str | None = None) -> Document:
    filename = file.filename or "uploaded-document"
    file_type = infer_file_type(filename)
    document_title = title or filename

    document = Document(
        workspace_id=workspace.id,
        title=document_title,
        filename=filename,
        file_type=file_type,
        status=DocumentStatus.PROCESSING,
    )
    db.add(document)
    db.flush()

    try:
        raw_text = await extract_text_from_upload(file)
        chunks = split_text(raw_text)

        document.raw_text = raw_text
        document.status = DocumentStatus.READY if chunks else DocumentStatus.FAILED

        for index, content in enumerate(chunks):
            db.add(
                DocumentChunk(
                    document_id=document.id,
                    workspace_id=workspace.id,
                    chunk_index=index,
                    content=content,
                    embedding=embed_text(content),
                    token_count=estimate_token_count(content),
                    metadata_={
                        "document_id": str(document.id),
                        "document_title": document.title,
                        "chunk_index": index,
                        "filename": filename,
                    },
                )
            )

        db.commit()
        db.refresh(document)
        return document
    except Exception:
        document.status = DocumentStatus.FAILED
        db.commit()
        db.refresh(document)
        raise


def list_documents(db: Session, workspace_id: UUID) -> list[Document]:
    query = select(Document).where(Document.workspace_id == workspace_id).order_by(Document.created_at.desc())
    return list(db.scalars(query))


def get_document(db: Session, document_id: UUID) -> Document | None:
    return db.get(Document, document_id)


def count_document_chunks(db: Session, document_id: UUID) -> int:
    return db.scalar(select(func.count()).select_from(DocumentChunk).where(DocumentChunk.document_id == document_id)) or 0


def list_document_chunks(db: Session, document_id: UUID) -> list[DocumentChunk]:
    query = (
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index.asc())
    )
    return list(db.scalars(query))


def delete_document(db: Session, document: Document) -> None:
    db.delete(document)
    db.commit()


def search_knowledge_base(db: Session, workspace_id: UUID, query: str, top_k: int = 5) -> list[tuple[DocumentChunk, str, float]]:
    query_embedding = embed_text(query)
    distance = DocumentChunk.embedding.cosine_distance(cast(query_embedding, Vector(1536)))
    stmt: Select = (
        select(DocumentChunk, Document.title, distance.label("distance"))
        .join(Document, DocumentChunk.document_id == Document.id)
        .where(DocumentChunk.workspace_id == workspace_id)
        .where(DocumentChunk.embedding.is_not(None))
        .order_by(distance.asc())
        .limit(max(1, min(top_k, 20)))
    )
    results = []
    for chunk, document_title, chunk_distance in db.execute(stmt).all():
        score = max(0.0, 1.0 - float(chunk_distance or 0.0))
        results.append((chunk, document_title, score))
    return results

