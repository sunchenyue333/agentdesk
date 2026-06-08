import enum
from uuid import UUID

from sqlalchemy import Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin, enum_values


class ApprovalStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EDITED = "edited"


class HumanApproval(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "human_approvals"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    agent_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    action_type: Mapped[str] = mapped_column(String(120), nullable=False)
    proposed_action_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    status: Mapped[ApprovalStatus] = mapped_column(
        Enum(ApprovalStatus, name="approval_status", values_callable=enum_values),
        default=ApprovalStatus.PENDING,
        index=True,
        nullable=False,
    )
    human_feedback: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace = relationship("Workspace", back_populates="human_approvals")
    agent_run = relationship("AgentRun", back_populates="human_approvals")
