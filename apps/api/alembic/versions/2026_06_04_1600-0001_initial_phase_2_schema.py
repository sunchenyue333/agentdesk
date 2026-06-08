"""initial phase 2 schema

Revision ID: 0001
Revises: None
Create Date: 2026-06-04 16:00:00.000000
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def timestamps() -> list[sa.Column]:
    return [
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    ]


def created_at() -> sa.Column:
    return sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False)


def uuid_pk() -> sa.Column:
    return sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False)


document_status = postgresql.ENUM(
    "uploaded", "processing", "ready", "failed", name="document_status", create_type=False
)
ticket_status = postgresql.ENUM(
    "open", "pending", "resolved", "closed", name="ticket_status", create_type=False
)
ticket_priority = postgresql.ENUM(
    "low", "medium", "high", "urgent", name="ticket_priority", create_type=False
)
ticket_message_role = postgresql.ENUM(
    "customer", "agent", "human", name="ticket_message_role", create_type=False
)
agent_run_status = postgresql.ENUM(
    "running",
    "completed",
    "failed",
    "waiting_for_approval",
    name="agent_run_status",
    create_type=False,
)
agent_step_status = postgresql.ENUM(
    "running", "completed", "failed", name="agent_step_status", create_type=False
)
tool_call_status = postgresql.ENUM(
    "running", "completed", "failed", name="tool_call_status", create_type=False
)
approval_status = postgresql.ENUM(
    "pending", "approved", "rejected", "edited", name="approval_status", create_type=False
)
eval_run_status = postgresql.ENUM(
    "pending", "running", "completed", "failed", name="eval_run_status", create_type=False
)


def create_enum_type(name: str, values: tuple[str, ...]) -> None:
    quoted_values = ", ".join(f"'{value}'" for value in values)
    op.execute(
        sa.text(
            f"""
            DO $$
            BEGIN
                CREATE TYPE {name} AS ENUM ({quoted_values});
            EXCEPTION WHEN duplicate_object THEN
                NULL;
            END $$;
            """
        )
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    create_enum_type("document_status", ("uploaded", "processing", "ready", "failed"))
    create_enum_type("ticket_status", ("open", "pending", "resolved", "closed"))
    create_enum_type("ticket_priority", ("low", "medium", "high", "urgent"))
    create_enum_type("ticket_message_role", ("customer", "agent", "human"))
    create_enum_type("agent_run_status", ("running", "completed", "failed", "waiting_for_approval"))
    create_enum_type("agent_step_status", ("running", "completed", "failed"))
    create_enum_type("tool_call_status", ("running", "completed", "failed"))
    create_enum_type("approval_status", ("pending", "approved", "rejected", "edited"))
    create_enum_type("eval_run_status", ("pending", "running", "completed", "failed"))

    op.create_table(
        "users",
        uuid_pk(),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])

    op.create_table(
        "workspaces",
        uuid_pk(),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        *timestamps(),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "documents",
        uuid_pk(),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("file_type", sa.String(length=40), nullable=False),
        sa.Column("status", document_status, nullable=False),
        sa.Column("raw_text", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_documents_workspace_id", "documents", ["workspace_id"])

    op.create_table(
        "tickets",
        uuid_pk(),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("customer_name", sa.String(length=160), nullable=False),
        sa.Column("customer_email", sa.String(length=255), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", ticket_status, nullable=False),
        sa.Column("priority", ticket_priority, nullable=False),
        *timestamps(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tickets_priority", "tickets", ["priority"])
    op.create_index("ix_tickets_status", "tickets", ["status"])
    op.create_index("ix_tickets_workspace_id", "tickets", ["workspace_id"])

    op.create_table(
        "eval_datasets",
        uuid_pk(),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=180), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        created_at(),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_datasets_workspace_id", "eval_datasets", ["workspace_id"])

    op.create_table(
        "document_chunks",
        uuid_pk(),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=True),
        sa.Column("token_count", sa.Integer(), nullable=True),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_chunks_document_id", "document_chunks", ["document_id"])
    op.create_index("ix_document_chunks_workspace_id", "document_chunks", ["workspace_id"])

    op.create_table(
        "ticket_messages",
        uuid_pk(),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", ticket_message_role, nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        created_at(),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_ticket_messages_ticket_id", "ticket_messages", ["ticket_id"])

    op.create_table(
        "agent_runs",
        uuid_pk(),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("input", sa.Text(), nullable=False),
        sa.Column("final_output", sa.Text(), nullable=True),
        sa.Column("status", agent_run_status, nullable=False),
        sa.Column("model", sa.String(length=120), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost", sa.Numeric(12, 6), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_runs_status", "agent_runs", ["status"])
    op.create_index("ix_agent_runs_user_id", "agent_runs", ["user_id"])
    op.create_index("ix_agent_runs_workspace_id", "agent_runs", ["workspace_id"])

    op.create_table(
        "eval_cases",
        uuid_pk(),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("expected_answer", sa.Text(), nullable=True),
        sa.Column("expected_sources", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tags", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        created_at(),
        sa.ForeignKeyConstraint(["dataset_id"], ["eval_datasets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_cases_dataset_id", "eval_cases", ["dataset_id"])

    op.create_table(
        "eval_runs",
        uuid_pk(),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", eval_run_status, nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("average_faithfulness", sa.Numeric(5, 4), nullable=True),
        sa.Column("average_answer_relevancy", sa.Numeric(5, 4), nullable=True),
        sa.Column("average_context_precision", sa.Numeric(5, 4), nullable=True),
        sa.Column("average_context_recall", sa.Numeric(5, 4), nullable=True),
        sa.ForeignKeyConstraint(["dataset_id"], ["eval_datasets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_runs_dataset_id", "eval_runs", ["dataset_id"])
    op.create_index("ix_eval_runs_status", "eval_runs", ["status"])
    op.create_index("ix_eval_runs_workspace_id", "eval_runs", ["workspace_id"])

    op.create_table(
        "agent_steps",
        uuid_pk(),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("step_name", sa.String(length=120), nullable=False),
        sa.Column("input_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("output_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("latency_ms", sa.Integer(), nullable=True),
        sa.Column("status", agent_step_status, nullable=False),
        sa.Column("error", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_agent_steps_agent_run_id", "agent_steps", ["agent_run_id"])

    op.create_table(
        "tool_calls",
        uuid_pk(),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_name", sa.String(length=120), nullable=False),
        sa.Column("tool_args_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("tool_result_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("status", tool_call_status, nullable=False),
        created_at(),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tool_calls_agent_run_id", "tool_calls", ["agent_run_id"])

    op.create_table(
        "human_approvals",
        uuid_pk(),
        sa.Column("workspace_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("agent_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.String(length=120), nullable=False),
        sa.Column("proposed_action_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("status", approval_status, nullable=False),
        sa.Column("human_feedback", sa.Text(), nullable=True),
        *timestamps(),
        sa.ForeignKeyConstraint(["agent_run_id"], ["agent_runs.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["workspace_id"], ["workspaces.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_human_approvals_agent_run_id", "human_approvals", ["agent_run_id"])
    op.create_index("ix_human_approvals_status", "human_approvals", ["status"])
    op.create_index("ix_human_approvals_workspace_id", "human_approvals", ["workspace_id"])

    op.create_table(
        "eval_results",
        uuid_pk(),
        sa.Column("eval_run_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("eval_case_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("generated_answer", sa.Text(), nullable=True),
        sa.Column("retrieved_context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("faithfulness", sa.Numeric(5, 4), nullable=True),
        sa.Column("answer_relevancy", sa.Numeric(5, 4), nullable=True),
        sa.Column("context_precision", sa.Numeric(5, 4), nullable=True),
        sa.Column("context_recall", sa.Numeric(5, 4), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        created_at(),
        sa.ForeignKeyConstraint(["eval_case_id"], ["eval_cases.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["eval_run_id"], ["eval_runs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_eval_results_eval_case_id", "eval_results", ["eval_case_id"])
    op.create_index("ix_eval_results_eval_run_id", "eval_results", ["eval_run_id"])


def downgrade() -> None:
    for table_name in [
        "eval_results",
        "human_approvals",
        "tool_calls",
        "agent_steps",
        "eval_runs",
        "eval_cases",
        "agent_runs",
        "ticket_messages",
        "document_chunks",
        "eval_datasets",
        "tickets",
        "documents",
        "workspaces",
        "users",
    ]:
        op.drop_table(table_name)

    for enum_name in [
        "eval_run_status",
        "approval_status",
        "tool_call_status",
        "agent_step_status",
        "agent_run_status",
        "ticket_message_role",
        "ticket_priority",
        "ticket_status",
        "document_status",
    ]:
        op.execute(sa.text(f"DROP TYPE IF EXISTS {enum_name}"))
