"""Experiment lifecycle: the one place that names its states and moves.

An experiment carries two persisted columns, ``stage`` and ``status``.
Together they form one state machine::

    create ──► (stage S, PENDING | IN_PROGRESS)

    advance  (non-terminal, stage < DOCUMENTATION):
        (S, PENDING | IN_PROGRESS) ──► (S+1, IN_PROGRESS)
    advance  (non-terminal, stage == DOCUMENTATION):
        (DOCUMENTATION, PENDING | IN_PROGRESS) ──► (DOCUMENTATION, COMPLETED)
                                                   + completed_at stamped
    fail     (non-terminal, any stage):
        (S, PENDING | IN_PROGRESS) ──► (S, FAILED)

    COMPLETED and FAILED are terminal: every transition out of them is refused.

Stages run in a fixed order::

    ideation → prediction → application → firing → analysis → documentation

The stored values (``"ideation"``, ``"in_progress"`` ...) are unchanged, so
existing databases read and write exactly as before.  Unknown stage values
already on disk are read as ``ideation`` (the historical fallback) rather
than crashing.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from .models import ExperimentStage, ExperimentStatus


class IllegalExperimentTransition(ValueError):
    """Raised when a move is not allowed from the experiment's current state."""


STAGE_ORDER: tuple[ExperimentStage, ...] = (
    ExperimentStage.IDEATION,
    ExperimentStage.PREDICTION,
    ExperimentStage.APPLICATION,
    ExperimentStage.FIRING,
    ExperimentStage.ANALYSIS,
    ExperimentStage.DOCUMENTATION,
)

ACTIVE_STATUSES: frozenset[ExperimentStatus] = frozenset(
    {ExperimentStatus.PENDING, ExperimentStatus.IN_PROGRESS}
)
TERMINAL_STATUSES: frozenset[ExperimentStatus] = frozenset(
    {ExperimentStatus.COMPLETED, ExperimentStatus.FAILED}
)

#: Columns only the transition functions below may write.
LIFECYCLE_COLUMNS: frozenset[str] = frozenset({"stage", "status", "completed_at"})


def parse_stage(value: Optional[str]) -> ExperimentStage:
    """Read a stored stage, tolerating unknown legacy values (→ ideation)."""
    try:
        return ExperimentStage(value)
    except ValueError:
        return ExperimentStage.IDEATION


def parse_status(value: Optional[str]) -> ExperimentStatus:
    """Read a stored status, tolerating unknown legacy values (→ pending)."""
    try:
        return ExperimentStatus(value)
    except ValueError:
        return ExperimentStatus.PENDING


def stage_index(stage: Optional[str]) -> int:
    """Position of ``stage`` in the pipeline (unknown values count as 0)."""
    return STAGE_ORDER.index(parse_stage(stage))


@dataclass(frozen=True)
class ExperimentState:
    """A snapshot of the lifecycle columns."""

    stage: ExperimentStage
    status: ExperimentStatus

    @classmethod
    def read(cls, stage: Optional[str], status: Optional[str]) -> "ExperimentState":
        return cls(parse_stage(stage), parse_status(status))

    @property
    def is_terminal(self) -> bool:
        return self.status in TERMINAL_STATUSES


def validate_initial(stage: Optional[str], status: Optional[str]) -> dict:
    """Check the state a new experiment is created in.

    New experiments may start at any stage but must be PENDING or
    IN_PROGRESS; creating one already finished is refused.
    Returns the column values to store.
    """
    try:
        st = ExperimentStage(stage)
    except ValueError:
        raise IllegalExperimentTransition(f"Unknown experiment stage: {stage!r}")
    try:
        ss = ExperimentStatus(status)
    except ValueError:
        raise IllegalExperimentTransition(f"Unknown experiment status: {status!r}")
    if ss not in ACTIVE_STATUSES:
        raise IllegalExperimentTransition(
            f"New experiments must be pending or in_progress, not {ss.value!r}"
        )
    return {"stage": st.value, "status": ss.value}


def _now() -> str:
    return datetime.now().isoformat()


def advance(state: ExperimentState) -> dict:
    """Column updates for moving one step forward. Refuses terminal states."""
    if state.is_terminal:
        raise IllegalExperimentTransition(
            f"Cannot advance a {state.status.value} experiment"
        )
    idx = STAGE_ORDER.index(state.stage)
    if idx == len(STAGE_ORDER) - 1:
        return {"status": ExperimentStatus.COMPLETED.value, "completed_at": _now()}
    return {
        "stage": STAGE_ORDER[idx + 1].value,
        "status": ExperimentStatus.IN_PROGRESS.value,
    }


def fail(state: ExperimentState) -> dict:
    """Column updates for marking an active experiment failed."""
    if state.is_terminal:
        raise IllegalExperimentTransition(
            f"Cannot fail a {state.status.value} experiment"
        )
    return {"status": ExperimentStatus.FAILED.value}


def start(state: ExperimentState) -> dict:
    """Column updates for PENDING → IN_PROGRESS without changing stage."""
    if state.status is not ExperimentStatus.PENDING:
        raise IllegalExperimentTransition(
            f"Cannot start a {state.status.value} experiment"
        )
    return {"status": ExperimentStatus.IN_PROGRESS.value}


def complete(state: ExperimentState) -> dict:
    """Column updates for finishing; only legal from the final stage."""
    if state.is_terminal or state.stage is not STAGE_ORDER[-1]:
        raise IllegalExperimentTransition(
            f"Cannot complete a {state.status.value} experiment at "
            f"stage {state.stage.value!r}"
        )
    return advance(state)


def transition_for_status(state: ExperimentState, target: str) -> dict:
    """Map a requested target status onto the one named transition for it."""
    try:
        wanted = ExperimentStatus(target)
    except ValueError:
        raise IllegalExperimentTransition(f"Unknown experiment status: {target!r}")
    moves = {
        ExperimentStatus.PENDING: None,
        ExperimentStatus.IN_PROGRESS: start,
        ExperimentStatus.COMPLETED: complete,
        ExperimentStatus.FAILED: fail,
    }
    move = moves[wanted]
    if move is None:
        raise IllegalExperimentTransition("Experiments cannot move back to pending")
    return move(state)
