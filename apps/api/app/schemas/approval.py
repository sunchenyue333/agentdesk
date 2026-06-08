from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.approval import ApprovalStatus
from app.models.agent import AgentRunStatus


class ApprovalDecisionRequest(BaseModel):
    human_feedback: str | None = None
    edited_action_json: dict | None = None


class ApprovalActionResponse(BaseModel):
    approval_id: UUID
    status: ApprovalStatus
    executed_result_json: dict | None = None


class ApprovalAgentRunRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    input: str
    final_output: str | None
    status: AgentRunStatus
    model: str | None
    latency_ms: int | None
    created_at: datetime
    updated_at: datetime


class ApprovalRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    agent_run_id: UUID
    action_type: str
    proposed_action_json: dict
    status: ApprovalStatus
    human_feedback: str | None
    created_at: datetime
    updated_at: datetime
    agent_run: ApprovalAgentRunRead


class ApprovalListResponse(BaseModel):
    approvals: list[ApprovalRead] = Field(default_factory=list)
