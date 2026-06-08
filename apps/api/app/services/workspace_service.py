from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.workspace import Workspace

DEMO_WORKSPACE_NAME = "Acme SaaS Support"


def get_or_create_demo_workspace(db: Session) -> Workspace:
    workspace = db.scalar(select(Workspace).where(Workspace.name == DEMO_WORKSPACE_NAME))
    if workspace is not None:
        return workspace

    workspace = Workspace(
        name=DEMO_WORKSPACE_NAME,
        description="Demo support workspace for AgentDesk.",
    )
    db.add(workspace)
    db.commit()
    db.refresh(workspace)
    return workspace


def list_workspaces(db: Session) -> list[Workspace]:
    get_or_create_demo_workspace(db)
    return list(db.scalars(select(Workspace).order_by(Workspace.created_at.asc())))

