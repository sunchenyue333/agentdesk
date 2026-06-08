from langgraph.graph import END, StateGraph
from sqlalchemy.orm import Session

from app.agents.state import SupportAgentState
from app.agents.tools import knowledge_search
from app.models.workspace import Workspace

RISK_KEYWORDS = ("refund", "legal", "medical", "finance", "security", "privacy", "credit card")
TICKET_KEYWORDS = ("ticket", "issue", "bug", "cannot", "can't", "error", "problem", "login")


def classify_intent(state: SupportAgentState) -> SupportAgentState:
    message = state["user_message"].lower()
    if any(keyword in message for keyword in ("refund", "pricing", "password", "security", "policy")):
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
        result = knowledge_search(db, state["workspace_id"], state["user_message"], top_k=5)
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
    chunks = state.get("retrieved_chunks", [])
    citations = [
        {
            "document_id": chunk["document_id"],
            "document_title": chunk["document_title"],
            "chunk_id": chunk["chunk_id"],
            "quote": chunk["content"][:220],
        }
        for chunk in chunks[:3]
    ]

    if chunks:
        evidence = "\n\n".join(chunk["content"][:700] for chunk in chunks[:3])
        answer = (
            "Based on the available support knowledge, here is the best answer:\n\n"
            f"{summarize_from_context(state['user_message'], evidence)}\n\n"
            "Sources are attached below."
        )
        confidence = "medium"
    else:
        answer = "I do not have enough knowledge base context to answer confidently. Please escalate this to a human."
        confidence = "low"

    steps = state.get("structured_steps", [])
    steps.append({"title": "Answer drafted", "detail": f"confidence={confidence}"})
    return {
        **state,
        "draft_answer": answer,
        "final_answer": answer,
        "citations": citations,
        "confidence": confidence,
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
    final_answer = (
        f"{state.get('final_answer', '')}\n\n"
        "This response or proposed action should be reviewed by a human before sending to the customer."
    )
    return {**state, "final_answer": final_answer, "structured_steps": steps}


def final_response(state: SupportAgentState) -> SupportAgentState:
    steps = state.get("structured_steps", [])
    steps.append({"title": "Final response ready", "detail": "structured trace saved"})
    return {**state, "structured_steps": steps}


def summarize_from_context(question: str, evidence: str) -> str:
    question_terms = {term.strip(".,?!:;").lower() for term in question.split() if len(term) > 3}
    sentences = [sentence.strip() for sentence in evidence.replace("\n", " ").split(".") if sentence.strip()]
    ranked = sorted(
        sentences,
        key=lambda sentence: sum(term in sentence.lower() for term in question_terms),
        reverse=True,
    )
    selected = ranked[:3] or sentences[:2]
    return ". ".join(selected).strip() + ("." if selected else "")


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

