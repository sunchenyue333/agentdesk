from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents.answer_generation import generate_grounded_answer
from app.agents.state import SupportAgentState
from app.agents.tools import knowledge_search
from app.core.config import settings
from app.models.workspace import Workspace

RISK_KEYWORDS = ("refund", "legal", "medical", "finance", "security", "privacy", "credit card", "退款")
TICKET_KEYWORDS = ("ticket", "issue", "bug", "cannot", "can't", "error", "problem", "login", "工单")


def classify_intent(state: SupportAgentState) -> SupportAgentState:
    message = state["user_message"].lower()
    if any(keyword in message for keyword in ("refund", "pricing", "password", "security", "policy", "密码", "退款", "安全", "政策")):
        intent = "knowledge_question"
    elif any(keyword in message for keyword in TICKET_KEYWORDS):
        intent = "support_ticket"
    else:
        intent = "general_support"
    return {
        **state,
        "intent": intent,
        "structured_steps": [
            {"title": "Intent classified", "detail": intent},
        ],
    }


def retrieve_context_factory(db: Session):
    def retrieve_context(state: SupportAgentState) -> SupportAgentState:
        result = knowledge_search(db, state["workspace_id"], state["user_message"], top_k=3)
        steps = state.get("structured_steps", [])
        steps.append({"title": "Knowledge retrieved", "detail": f"Found {len(result['chunks'])} chunks"})
        return {**state, "retrieved_chunks": result["chunks"], "structured_steps": steps}

    return retrieve_context


def decide_action(state: SupportAgentState) -> SupportAgentState:
    message = state["user_message"].lower()
    selected_tool = "create_ticket" if any(keyword in message for keyword in TICKET_KEYWORDS) else None
    risk_level = "medium" if any(keyword in message for keyword in RISK_KEYWORDS) else "low"
    approval_required = risk_level == "medium" or selected_tool == "create_ticket"
    steps = state.get("structured_steps", [])
    steps.append(
        {
            "title": "Action decided",
            "detail": selected_tool or "answer_from_knowledge_base",
        }
    )
    steps.append({"title": "Risk checked", "detail": f"{risk_level}, approval_required={approval_required}"})
    return {
        **state,
        "selected_tool": selected_tool,
        "risk_level": risk_level,
        "approval_required": approval_required,
        "approval_status": "pending" if approval_required else None,
        "structured_steps": steps,
    }


def generate_answer(state: SupportAgentState) -> SupportAgentState:
    result = generate_grounded_answer(
        state["user_message"],
        state.get("retrieved_chunks", []),
        openai_api_key=settings.openai_api_key,
    )
    answer = result["answer"]
    confidence = result["confidence"]

    steps = state.get("structured_steps", [])
    steps.append({"title": "Answer drafted", "detail": f"confidence={confidence}"})
    return {
        **state,
        "draft_answer": answer,
        "final_answer": answer,
        "citations": result["citations"],
        "confidence": confidence,
        "answer_mode": result["answer_mode"],
        "retrieved_chunks": result["relevant_chunks"],
        "structured_steps": steps,
    }


def maybe_call_tool_factory(db: Session, workspace: Workspace):
    def maybe_call_tool(state: SupportAgentState) -> SupportAgentState:
        if state.get("selected_tool") != "create_ticket":
            return state

        result = {
            "status": "pending_approval",
            "reason": "Ticket creation is proposed by the agent and requires human approval in this phase.",
        }
        steps = state.get("structured_steps", [])
        steps.append({"title": "Tool prepared", "detail": "create_ticket pending human approval"})
        return {
            **state,
            "tool_args": {
                "workspace_id": str(workspace.id),
                "customer_name": "Demo Customer",
                "customer_email": "customer@example.com",
                "title": state["user_message"][:80],
                "description": state["user_message"],
                "priority": "medium",
            },
            "tool_result": result,
            "structured_steps": steps,
        }

    return maybe_call_tool


def maybe_request_human_approval(state: SupportAgentState) -> SupportAgentState:
    if not state.get("approval_required"):
        return state
    steps = state.get("structured_steps", [])
    steps.append({"title": "Human approval requested", "detail": "high-risk or customer-facing action"})
    return {**state, "structured_steps": steps}


def final_response(state: SupportAgentState) -> SupportAgentState:
    steps = state.get("structured_steps", [])
    steps.append({"title": "Final response ready", "detail": "structured trace saved"})
    return {**state, "structured_steps": steps}


def build_support_agent(db: Session, workspace: Workspace):
    graph = StateGraph(SupportAgentState)
    graph.add_node("classify_intent", classify_intent)
    graph.add_node("retrieve_context", retrieve_context_factory(db))
    graph.add_node("decide_action", decide_action)
    graph.add_node("generate_answer", generate_answer)
    graph.add_node("maybe_call_tool", maybe_call_tool_factory(db, workspace))
    graph.add_node("maybe_request_human_approval", maybe_request_human_approval)
    graph.add_node("final_response", final_response)

    graph.set_entry_point("classify_intent")
    graph.add_edge("classify_intent", "retrieve_context")
    graph.add_edge("retrieve_context", "decide_action")
    graph.add_edge("decide_action", "generate_answer")
    graph.add_edge("generate_answer", "maybe_call_tool")
    graph.add_edge("maybe_call_tool", "maybe_request_human_approval")
    graph.add_edge("maybe_request_human_approval", "final_response")
    graph.add_edge("final_response", END)
    return graph.compile()
