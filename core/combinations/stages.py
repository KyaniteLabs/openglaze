"""Combination pipeline stage: the one place that names its states and moves.

The ``combinations.stage`` column tracks where a combo sits on the board::

    idea ⇄ predicting ⇄ testing ⇄ fired ⇄ documented     (manual board moves)

    any stage ──record_outcome(confirmed | surprise)──► documented
                (also sets type and prediction_grade to the outcome)

Manual moves between the five canonical stages are free (the board lets a
potter drag a card anywhere); writing any other value is refused.
Recording a firing outcome is the only automatic move and always lands on
``documented``.

Older rows and older readers used ``tested``, ``proven`` and ``confirmed`` as
stage values. They are never written any more but are still read as
"has been fired" so existing data keeps counting.
"""

from __future__ import annotations

import sqlite3
from enum import Enum


class CombinationStage(str, Enum):
    """Canonical values of ``combinations.stage``."""

    IDEA = "idea"
    PREDICTING = "predicting"
    TESTING = "testing"
    FIRED = "fired"
    DOCUMENTED = "documented"


class FiringOutcome(str, Enum):
    """Outcomes that close a combination's pipeline."""

    CONFIRMED = "confirmed"
    SURPRISE = "surprise"


class IllegalStageTransition(ValueError):
    """Raised when a stage write is not a legal move."""


INITIAL_STAGE = CombinationStage.IDEA

#: Legacy stage values that may exist on disk; read-only.
LEGACY_FIRED_STAGES: frozenset[str] = frozenset({"tested", "proven", "confirmed"})

#: Stages that mean "this combo has been fired", including legacy values.
FIRED_STAGE_VALUES: tuple[str, ...] = (
    CombinationStage.FIRED.value,
    CombinationStage.DOCUMENTED.value,
    *sorted(LEGACY_FIRED_STAGES),
)


def has_been_fired(stage: str | None) -> bool:
    """True if a stored stage (canonical or legacy) means the combo was fired."""
    return stage in FIRED_STAGE_VALUES


def validate_stage(value: object) -> str:
    """Return ``value`` if it is a canonical stage a writer may store."""
    try:
        return CombinationStage(value).value
    except ValueError:
        allowed = ", ".join(s.value for s in CombinationStage)
        raise IllegalStageTransition(
            f"Unknown combination stage {value!r}; expected one of: {allowed}"
        )


def outcome_updates(outcome: str, result: str | None = None) -> dict:
    """Column updates for recording a firing outcome on a combination."""
    try:
        o = FiringOutcome(outcome)
    except ValueError:
        raise IllegalStageTransition(f"Unknown firing outcome: {outcome!r}")
    updates = {
        "type": o.value,
        "prediction_grade": o.value,
        "stage": CombinationStage.DOCUMENTED.value,
    }
    if result is not None:
        updates["result"] = result
    return updates


def count_fired(cursor: sqlite3.Cursor, user_id: str) -> int:
    """How many of ``user_id``'s combinations have been fired (any era's value)."""
    placeholders = ", ".join("?" for _ in FIRED_STAGE_VALUES)
    cursor.execute(
        "SELECT COUNT(*) FROM combinations "  # nosec B608
        f"WHERE user_id = ? AND stage IN ({placeholders})",
        (user_id, *FIRED_STAGE_VALUES),
    )
    return cursor.fetchone()[0]
