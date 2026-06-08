from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.approval import ApprovalStatus
from app.models.workspace import Workspace
from app.schemas.approval import (
    ApprovalActionResponse,
    ApprovalDecisionRequest,
    ApprovalListResponse,
    ApprovalRead,
)
from app.services.approval_service import (
    approve_human_approval,
    get_approval,
    list_approvals,
    reject_human_approval,
)

router = APIRouter(tags=["approvals"])


@router.get("/workspaces/{workspace_id}/approvals", response_model=ApprovalListResponse)
def get_workspace_approvals(
    workspace_id: UUID,
    status: ApprovalStatus | None = Query(default=None),
    db: Session = Depends(get_db),
):
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return {"approvals": list_approvals(db, workspace_id, status)}


@router.get("/approvals/{approval_id}", response_model=ApprovalRead)
def get_approval_detail(approval_id: UUID, db: Session = Depends(get_db)):
    approval = get_approval(db, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/approvals/{approval_id}/approve", response_model=ApprovalActionResponse)
def approve_approval(
    approval_id: UUID,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    approval = get_approval(db, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    try:
        executed_result = approve_human_approval(db, approval, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "approval_id": approval.id,
        "status": approval.status,
        "executed_result_json": executed_result,
    }


@router.post("/approvals/{approval_id}/reject", response_model=ApprovalActionResponse)
def reject_approval(
    approval_id: UUID,
    payload: ApprovalDecisionRequest,
    db: Session = Depends(get_db),
):
    approval = get_approval(db, approval_id)
    if approval is None:
        raise HTTPException(status_code=404, detail="Approval not found")
    try:
        reject_human_approval(db, approval, payload)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
    return {
        "approval_id": approval.id,
        "status": approval.status,
        "executed_result_json": None,
    }
