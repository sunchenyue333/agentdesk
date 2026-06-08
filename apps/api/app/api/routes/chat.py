from time import perf_counter
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.agents.graph import build_support_agent
from app.core.config import settings
from app.core.database import get_db
from app.models.workspace import Workspace
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.tracing import complete_agent_run, create_agent_run

router = APIRouter(tags=["chat"])


@router.post("/workspaces/{workspace_id}/chat", response_model=ChatResponse)
def chat_with_agent(workspace_id: UUID, request: ChatRequest, db: Session = Depends(get_db)):
    workspace = db.get(Workspace, workspace_id)
    if workspace is None:
        raise HTTPException(status_code=404, detail="Workspace not found")

    started_at = perf_counter()
    run = create_agent_run(db, workspace_id, request.message, settings.openai_model)
    graph = build_support_agent(db, workspace)
    state = graph.invoke({"workspace_id": workspace_id, "user_message": request.message})
    run = complete_agent_run(db, run, state, started_at)

    return {
        "answer": state.get("final_answer", ""),
        "citations": state.get("citations", []),
        "confidence": state.get("confidence", "low"),
        "needs_human_review": bool(state.get("approval_required")),
        "agent_run_id": str(run.id),
        "steps": state.get("structured_steps", []),
        "tool_calls": [
            {
                "tool_name": call.tool_name,
                "tool_args_json": call.tool_args_json,
                "tool_result_json": call.tool_result_json,
                "status": call.status.value,
            }
            for call in run.tool_calls
        ],
        "latency_ms": run.latency_ms,
    }

