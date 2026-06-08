from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)


class ChatCitation(BaseModel):
    document_id: str
    document_title: str
    chunk_id: str
    heading: str
    quote: str


class ChatStep(BaseModel):
    title: str
    detail: str


class ChatToolCall(BaseModel):
    tool_name: str
    tool_args_json: dict | None
    tool_result_json: dict | None
    status: str


class ChatRetrievedChunk(BaseModel):
    chunk_id: str
    document_id: str
    document_title: str
    heading: str | None = None
    heading_path: list[str] = Field(default_factory=list)
    content: str
    score: float


class ChatResponse(BaseModel):
    answer: str
    citations: list[ChatCitation]
    confidence: str
    needs_human_review: bool
    answer_mode: str
    agent_run_id: str
    structured_steps: list[str]
    retrieved_chunks: list[ChatRetrievedChunk]
    tool_calls: list[ChatToolCall]
    latency_ms: int | None
