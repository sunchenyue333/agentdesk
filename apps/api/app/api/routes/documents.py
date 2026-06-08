from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.document import (
    DocumentChunkRead,
    DocumentDetail,
    DocumentRead,
    KnowledgeSearchRequest,
    KnowledgeSearchResponse,
)
from app.services.document_service import (
    count_document_chunks,
    delete_document,
    get_document,
    ingest_document,
    list_document_chunks,
    list_documents,
    search_knowledge_base,
)
from app.services.workspace_service import get_or_create_demo_workspace
from app.models.workspace import Workspace

router = APIRouter(tags=["documents"])


@router.get("/workspaces/{workspace_id}/documents", response_model=list[DocumentRead])
def get_documents(workspace_id: UUID, db: Session = Depends(get_db)) -> list:
    return list_documents(db, workspace_id)


@router.post("/workspaces/{workspace_id}/documents/upload", response_model=DocumentRead)
async def upload_document(
    workspace_id: UUID,
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    db: Session = Depends(get_db),
):
    workspace = get_or_create_demo_workspace(db)
    if workspace.id != workspace_id:
        workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    try:
        return await ingest_document(db, workspace, file, title)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/documents/{document_id}", response_model=DocumentDetail)
def get_document_detail(document_id: UUID, db: Session = Depends(get_db)):
    document = get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return DocumentDetail(
        id=document.id,
        workspace_id=document.workspace_id,
        title=document.title,
        filename=document.filename,
        file_type=document.file_type,
        status=document.status,
        raw_text=document.raw_text,
        created_at=document.created_at,
        updated_at=document.updated_at,
        chunk_count=count_document_chunks(db, document.id),
    )


@router.delete("/documents/{document_id}", status_code=204)
def remove_document(document_id: UUID, db: Session = Depends(get_db)) -> None:
    document = get_document(db, document_id)
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    delete_document(db, document)


@router.get("/documents/{document_id}/chunks", response_model=list[DocumentChunkRead])
def get_document_chunks(document_id: UUID, db: Session = Depends(get_db)) -> list:
    if get_document(db, document_id) is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return list_document_chunks(db, document_id)


@router.post("/workspaces/{workspace_id}/knowledge/search", response_model=KnowledgeSearchResponse)
def search_knowledge(workspace_id: UUID, request: KnowledgeSearchRequest, db: Session = Depends(get_db)):
    chunks = [
        {
            "chunk_id": chunk.id,
            "document_id": chunk.document_id,
            "document_title": document_title,
            "heading": (chunk.metadata_ or {}).get("heading"),
            "heading_path": (chunk.metadata_ or {}).get("heading_path", []),
            "content": chunk.content,
            "score": score,
        }
        for chunk, document_title, score in search_knowledge_base(db, workspace_id, request.query, request.top_k)
    ]
    return {"query": request.query, "chunks": chunks}
