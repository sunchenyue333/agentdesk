from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.ticket import TicketMessageRole, TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    customer_name: str = Field(min_length=1, max_length=160)
    customer_email: EmailStr
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1)
    priority: TicketPriority = TicketPriority.MEDIUM


class TicketUpdate(BaseModel):
    status: TicketStatus | None = None
    priority: TicketPriority | None = None
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1)


class TicketRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    workspace_id: UUID
    customer_name: str
    customer_email: str
    title: str
    description: str
    status: TicketStatus
    priority: TicketPriority
    created_at: datetime
    updated_at: datetime


class TicketMessageCreate(BaseModel):
    role: TicketMessageRole = TicketMessageRole.HUMAN
    content: str = Field(min_length=1)


class TicketMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    ticket_id: UUID
    role: TicketMessageRole
    content: str
    created_at: datetime


class TicketDetail(TicketRead):
    messages: list[TicketMessageRead]


class DraftTicketReplyRequest(BaseModel):
    tone: str = "professional"
    context: str | None = None


class DraftTicketReplyResponse(BaseModel):
    draft_reply: str

