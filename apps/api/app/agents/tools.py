from sqlalchemy.orm import Session

from app.models.workspace import Workspace
from app.schemas.ticket import TicketCreate
from app.services.document_service import search_knowledge_base
from app.services.ticket_service import create_ticket


def knowledge_search(db: Session, workspace_id, query: str, top_k: int = 3) -> dict:
    chunks = []
    for chunk, document_title, score in search_knowledge_base(db, workspace_id, query, top_k):
        chunks.append(
            {
                "chunk_id": str(chunk.id),
                "document_id": str(chunk.document_id),
                "document_title": document_title,
                "heading": (chunk.metadata_ or {}).get("heading"),
                "heading_path": (chunk.metadata_ or {}).get("heading_path", []),
                "content": chunk.content,
                "score": score,
            }
        )
    return {"chunks": chunks}


def create_support_ticket(
    db: Session,
    workspace: Workspace,
    customer_name: str,
    customer_email: str,
    title: str,
    description: str,
    priority: str = "medium",
) -> dict:
    ticket = create_ticket(
        db,
        workspace,
        TicketCreate(
            customer_name=customer_name,
            customer_email=customer_email,
            title=title,
            description=description,
            priority=priority,
        ),
    )
    return {"ticket_id": str(ticket.id), "status": ticket.status.value}
