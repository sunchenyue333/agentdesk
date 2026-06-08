from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.ticket import Ticket, TicketMessage, TicketMessageRole, TicketPriority, TicketStatus
from app.models.workspace import Workspace
from app.schemas.ticket import TicketCreate, TicketMessageCreate, TicketUpdate


def list_tickets(
    db: Session,
    workspace_id: UUID,
    status: TicketStatus | None = None,
    priority: TicketPriority | None = None,
) -> list[Ticket]:
    query = select(Ticket).where(Ticket.workspace_id == workspace_id)
    if status is not None:
        query = query.where(Ticket.status == status)
    if priority is not None:
        query = query.where(Ticket.priority == priority)
    query = query.order_by(Ticket.created_at.desc())
    return list(db.scalars(query))


def create_ticket(db: Session, workspace: Workspace, payload: TicketCreate) -> Ticket:
    ticket = Ticket(workspace_id=workspace.id, **payload.model_dump())
    db.add(ticket)
    db.flush()
    db.add(
        TicketMessage(
            ticket_id=ticket.id,
            role=TicketMessageRole.CUSTOMER,
            content=payload.description,
        )
    )
    db.commit()
    db.refresh(ticket)
    return ticket


def get_ticket(db: Session, ticket_id: UUID) -> Ticket | None:
    return db.scalar(
        select(Ticket)
        .options(selectinload(Ticket.messages))
        .where(Ticket.id == ticket_id)
    )


def update_ticket(db: Session, ticket: Ticket, payload: TicketUpdate) -> Ticket:
    updates = payload.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(ticket, field, value)
    db.commit()
    db.refresh(ticket)
    return ticket


def add_ticket_message(db: Session, ticket: Ticket, payload: TicketMessageCreate) -> TicketMessage:
    message = TicketMessage(ticket_id=ticket.id, role=payload.role, content=payload.content)
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def draft_ticket_reply(ticket: Ticket, tone: str = "professional", context: str | None = None) -> str:
    latest_customer_message = next(
        (message.content for message in sorted(ticket.messages, key=lambda item: item.created_at, reverse=True)
         if message.role == TicketMessageRole.CUSTOMER),
        ticket.description,
    )
    context_line = f"\n\nRelevant context: {context.strip()}" if context and context.strip() else ""
    return (
        f"Hi {ticket.customer_name},\n\n"
        f"Thanks for reaching out about \"{ticket.title}\". "
        f"I reviewed your message: {latest_customer_message.strip()}\n\n"
        f"We are looking into this and will follow up with the next best step shortly."
        f"{context_line}\n\n"
        f"Best,\nAcme SaaS Support\n\n"
        f"Tone: {tone}"
    )

