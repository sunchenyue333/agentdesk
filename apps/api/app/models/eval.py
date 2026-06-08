import enum
from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, CreatedAtMixin, UUIDPrimaryKeyMixin, enum_values


class EvalRunStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class EvalDataset(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "eval_datasets"

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    workspace = relationship("Workspace", back_populates="eval_datasets")
    cases = relationship("EvalCase", back_populates="dataset", cascade="all, delete-orphan")
    runs = relationship("EvalRun", back_populates="dataset", cascade="all, delete-orphan")


class EvalCase(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "eval_cases"

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("eval_datasets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    expected_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    expected_sources: Mapped[list | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    dataset = relationship("EvalDataset", back_populates="cases")
    results = relationship("EvalResult", back_populates="eval_case")


class EvalRun(UUIDPrimaryKeyMixin, Base):
    __tablename__ = "eval_runs"

    dataset_id: Mapped[UUID] = mapped_column(
        ForeignKey("eval_datasets.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    status: Mapped[EvalRunStatus] = mapped_column(
        Enum(EvalRunStatus, name="eval_run_status", values_callable=enum_values),
        default=EvalRunStatus.PENDING,
        index=True,
        nullable=False,
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    average_faithfulness: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    average_answer_relevancy: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    average_context_precision: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    average_context_recall: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)

    dataset = relationship("EvalDataset", back_populates="runs")
    workspace = relationship("Workspace", back_populates="eval_runs")
    results = relationship("EvalResult", back_populates="eval_run", cascade="all, delete-orphan")


class EvalResult(UUIDPrimaryKeyMixin, CreatedAtMixin, Base):
    __tablename__ = "eval_results"

    eval_run_id: Mapped[UUID] = mapped_column(
        ForeignKey("eval_runs.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    eval_case_id: Mapped[UUID] = mapped_column(
        ForeignKey("eval_cases.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    question: Mapped[str] = mapped_column(Text, nullable=False)
    generated_answer: Mapped[str | None] = mapped_column(Text, nullable=True)
    retrieved_context_json: Mapped[dict | list | None] = mapped_column(JSONB, nullable=True)
    faithfulness: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    answer_relevancy: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    context_precision: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    context_recall: Mapped[float | None] = mapped_column(Numeric(5, 4), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)

    eval_run = relationship("EvalRun", back_populates="results")
    eval_case = relationship("EvalCase", back_populates="results")
