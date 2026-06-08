from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ticket import TicketPriority, TicketStatus
from app.models.workspace import Workspace
from app.schemas.ticket import (
    DraftTicketReplyRequest,
    DraftTicketReplyResponse,
    TicketCreate,
    TicketDetail,
    TicketMessageCreate,
    TicketMessageRead,
    TicketRead,
    TicketUpdate,
)
from app.services.ticket_service import (
    add_ticket_message,
    create_ticket,
    draft_ticket_reply,
    get_ticket,
    list_tickets,
    update_ticket,
)

router = APIRouter(tags=["tickets"])


@router.get("/workspaces/{workspace_id}/tickets", response_model=list[TicketRead])
def get_tickets(
    workspace_id: UUID,
    status: TicketStatus | None = Query(default=None),
    priority: TicketPriority | None = Query(default=None),
    db: Session = Depends(get_db),
) -> list:
    return list_tickets(db, workspace_id, status, priority)


@router.post("/workspaces/{workspace_id}/tickets", response_model=TicketRead)
def post_ticket(workspace_id: UUID, payload: TicketCreate, db: Session = Depends(get_db)):
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return create_ticket(db, workspace, payload)


@router.get("/tickets/{ticket_id}", response_model=TicketDetail)
def get_ticket_detail(ticket_id: UUID, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket


@router.patch("/tickets/{ticket_id}", response_model=TicketRead)
def patch_ticket(ticket_id: UUID, payload: TicketUpdate, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return update_ticket(db, ticket, payload)


@router.post("/tickets/{ticket_id}/messages", response_model=TicketMessageRead)
def post_ticket_message(ticket_id: UUID, payload: TicketMessageCreate, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return add_ticket_message(db, ticket, payload)


@router.post("/tickets/{ticket_id}/draft-reply", response_model=DraftTicketReplyResponse)
def post_draft_reply(ticket_id: UUID, payload: DraftTicketReplyRequest, db: Session = Depends(get_db)):
    ticket = get_ticket(db, ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return {"draft_reply": draft_ticket_reply(ticket, payload.tone, payload.context)}

