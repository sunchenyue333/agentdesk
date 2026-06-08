from datetime import UTC, datetime
from time import perf_counter
from uuid import UUID

from sqlalchemy.orm import Session

from app.agents.state import SupportAgentState
from app.models.agent import AgentRun, AgentRunStatus, AgentStep, StepStatus, ToolCall, ToolCallStatus
from app.services.approval_service import create_human_approval_for_run


def create_agent_run(db: Session, workspace_id: UUID, user_message: str, model: str) -> AgentRun:
    run = AgentRun(
        workspace_id=workspace_id,
        input=user_message,
        status=AgentRunStatus.RUNNING,
        model=model,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run


def complete_agent_run(db: Session, run: AgentRun, state: SupportAgentState, started_at: float) -> AgentRun:
    run.final_output = state.get("final_answer")
    run.status = AgentRunStatus.WAITING_FOR_APPROVAL if state.get("approval_required") else AgentRunStatus.COMPLETED
    run.latency_ms = int((perf_counter() - started_at) * 1000)
    run.prompt_tokens = max(1, len(run.input) // 4)
    run.completion_tokens = max(1, len((run.final_output or "")) // 4)
    run.total_tokens = (run.prompt_tokens or 0) + (run.completion_tokens or 0)
    run.estimated_cost = 0

    now = datetime.now(UTC)
    for index, step in enumerate(state.get("structured_steps", [])):
        db.add(
            AgentStep(
                agent_run_id=run.id,
                step_name=step["title"],
                input_json={"order": index},
                output_json={"detail": step["detail"]},
                started_at=now,
                ended_at=now,
                latency_ms=0,
                status=StepStatus.COMPLETED,
            )
        )

    if state.get("selected_tool"):
        db.add(
            ToolCall(
                agent_run_id=run.id,
                tool_name=state["selected_tool"],
                tool_args_json=state.get("tool_args"),
                tool_result_json=state.get("tool_result"),
                status=ToolCallStatus.COMPLETED,
            )
        )

    create_human_approval_for_run(db, run, state)

    db.commit()
    db.refresh(run)
    return run
