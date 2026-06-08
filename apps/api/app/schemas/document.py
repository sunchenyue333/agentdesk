from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.document import DocumentStatus


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    title: str
    filename: str
    file_type: str
    status: DocumentStatus
    created_at: datetime
    updated_at: datetime


class DocumentDetail(DocumentRead):
    raw_text: str | None
    chunk_count: int


class DocumentChunkRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    document_id: UUID
    workspace_id: UUID
    chunk_index: int
    content: str
    token_count: int | None
    metadata_: dict | None
    created_at: datetime


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 3


class KnowledgeSearchChunk(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    heading: str | None = None
    heading_path: list[str] = Field(default_factory=list)
    content: str
    score: float


class KnowledgeSearchResponse(BaseModel):
    query: str
    chunks: list[KnowledgeSearchChunk]
