from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    documents = relationship("Document", back_populates="workspace", cascade="all, delete-orphan")
    document_chunks = relationship(
        "DocumentChunk",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    tickets = relationship("Ticket", back_populates="workspace", cascade="all, delete-orphan")
    agent_runs = relationship("AgentRun", back_populates="workspace", cascade="all, delete-orphan")
    human_approvals = relationship(
        "HumanApproval",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    eval_datasets = relationship(
        "EvalDataset",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    eval_runs = relationship("EvalRun", back_populates="workspace", cascade="all, delete-orphan")

