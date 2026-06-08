from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.workspace import WorkspaceRead
from app.services.workspace_service import get_or_create_demo_workspace, list_workspaces

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceRead])
def get_workspaces(db: Session = Depends(get_db)) -> list:
    return list_workspaces(db)


@router.get("/demo", response_model=WorkspaceRead)
def get_demo_workspace(db: Session = Depends(get_db)):
    return get_or_create_demo_workspace(db)

