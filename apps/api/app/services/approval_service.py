from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.agent import AgentRun, AgentRunStatus, ToolCall
from app.models.approval import ApprovalStatus, HumanApproval
from app.models.workspace import Workspace
from app.schemas.approval import ApprovalDecisionRequest
from app.schemas.ticket import TicketCreate
from app.services.ticket_service import create_ticket


def create_human_approval_for_run(db: Session, run: AgentRun, state: dict) -> HumanApproval | None:
    if not state.get("approval_required"):
        return None

    action_type = state.get("selected_tool") or "answer_review"
    approval = HumanApproval(
        workspace_id=run.workspace_id,
        agent_run_id=run.id,
        action_type=action_type,
        proposed_action_json={
            "risk_level": state.get("risk_level"),
            "answer": state.get("final_answer"),
            "selected_tool": state.get("selected_tool"),
            "tool_args": state.get("tool_args"),
            "tool_result": state.get("tool_result"),
            "confidence": state.get("confidence"),
            "citations": state.get("citations", []),
        },
        status=ApprovalStatus.PENDING,
    )
    db.add(approval)
    return approval


def list_approvals(
    db: Session,
    workspace_id: UUID,
    status: ApprovalStatus | None = ApprovalStatus.PENDING,
) -> list[HumanApproval]:
    query = (
        select(HumanApproval)
        .options(selectinload(HumanApproval.agent_run))
        .where(HumanApproval.workspace_id == workspace_id)
        .order_by(HumanApproval.created_at.desc())
    )
    if status is not None:
        query = query.where(HumanApproval.status == status)
    return list(db.scalars(query))


def get_approval(db: Session, approval_id: UUID) -> HumanApproval | None:
    return db.scalar(
        select(HumanApproval)
        .options(selectinload(HumanApproval.agent_run).selectinload(AgentRun.tool_calls))
        .where(HumanApproval.id == approval_id)
    )


def approve_human_approval(
    db: Session,
    approval: HumanApproval,
    payload: ApprovalDecisionRequest,
) -> dict | None:
    if approval.status != ApprovalStatus.PENDING:
        raise ValueError("Approval has already been reviewed")

    action_json = payload.edited_action_json or approval.proposed_action_json
    executed_result = _execute_approved_action(db, approval, action_json)

    approval.status = ApprovalStatus.EDITED if payload.edited_action_json else ApprovalStatus.APPROVED
    approval.human_feedback = payload.human_feedback
    approval.agent_run.status = AgentRunStatus.COMPLETED
    db.commit()
    db.refresh(approval)
    return executed_result


def reject_human_approval(
    db: Session,
    approval: HumanApproval,
    payload: ApprovalDecisionRequest,
) -> None:
    if approval.status != ApprovalStatus.PENDING:
        raise ValueError("Approval has already been reviewed")

    approval.status = ApprovalStatus.REJECTED
    approval.human_feedback = payload.human_feedback
    approval.agent_run.status = AgentRunStatus.COMPLETED
    db.commit()
    db.refresh(approval)


def _execute_approved_action(db: Session, approval: HumanApproval, action_json: dict) -> dict | None:
    selected_tool = action_json.get("selected_tool")
    if selected_tool != "create_ticket":
        return {"status": "approved_for_send"}

    workspace = db.get(Workspace, approval.workspace_id)
    if workspace is None:
        raise ValueError("Workspace not found")

    tool_args = action_json.get("tool_args") or {}
    ticket = create_ticket(db, workspace, TicketCreate.model_validate(tool_args))
    result = {"status": "executed", "ticket_id": str(ticket.id)}

    tool_call = _latest_tool_call(approval.agent_run, selected_tool)
    if tool_call is not None:
        tool_call.tool_result_json = result
        db.add(tool_call)
    return result


def _latest_tool_call(agent_run: AgentRun, tool_name: str) -> ToolCall | None:
    matching_calls = [call for call in agent_run.tool_calls if call.tool_name == tool_name]
    if not matching_calls:
        return None
    return matching_calls[-1]
