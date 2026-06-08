import enum
from uuid import UUID

from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class AgentRunStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    WAITING_FOR_APPROVAL = "waiting_for_approval"


class StepStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class ToolCallStatus(str, enum.Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class AgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "agent_runs"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    user_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    input: Mapped[str] = mapped_column(Text, nullable=False)
    final_output: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[AgentRunStatus] = mapped_column(
        Enum(AgentRunStatus, name="agent_run_status", values_callable=enum_values),
        default=AgentRunStatus.RUNNING,
        index=True,
        nullable=False,
    )
    model: Mapped[str | None] = mapped_column(String(120), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    prompt_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completion_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[int | None] = mapped_column(Integer, nullable=True)
    estimated_cost: Mapped[float | None] = mapped_column(Numeric(12, 6), nullable=True)

    workspace = relationship("Workspace", back_populates="agent_runs")
    user = relationship("User", back_populates="agent_runs")
    steps = relationship("AgentStep", back_populates="agent_run", cascade="all, delete-orphan")
    tool_calls = relationship("ToolCall", back_populates="agent_run", cascade="all, delete-orphan")
    human_approvals = relationship("HumanApproval", back_populates="agent_run")


class AgentStep(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "agent_steps"

    agent_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    step_name: Mapped[str] = mapped_column(String(120), nullable=False)
    input_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[StepStatus] = mapped_column(
        Enum(StepStatus, name="agent_step_status", values_callable=enum_values),
        default=StepStatus.RUNNING,
        nullable=False,
    )
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    agent_run = relationship("AgentRun", back_populates="steps")


class ToolCall(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "tool_calls"

    agent_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    tool_name: Mapped[str] = mapped_column(String(120), nullable=False)
    tool_args_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    tool_result_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    status: Mapped[ToolCallStatus] = mapped_column(
        Enum(ToolCallStatus, name="tool_call_status", values_callable=enum_values),
        default=ToolCallStatus.RUNNING,
        nullable=False,
    )

    agent_run = relationship("AgentRun", back_populates="tool_calls")
