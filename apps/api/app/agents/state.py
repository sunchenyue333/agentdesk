from typing import Any, TypedDict
from uuid import UUID


class Citation(TypedDict):
    document_id: str
    document_title: str
    chunk_id: str
    quote: str


class StructuredStep(TypedDict):
    title: str
    detail: str


class SupportAgentState(TypedDict, total=False):
    workspace_id: UUID
    user_message: str
    intent: str
    retrieved_chunks: list[dict[str, Any]]
    draft_answer: str
    selected_tool: str | None
    tool_args: dict[str, Any] | None
    tool_result: dict[str, Any] | None
    risk_level: str
    approval_required: bool
    approval_status: str | None
    final_answer: str
    citations: list[Citation]
    confidence: str
    structured_steps: list[StructuredStep]
    error: str | None

