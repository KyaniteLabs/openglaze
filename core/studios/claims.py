"""Lab-queue claim lifecycle: the one place that names its states and moves.

Each row in ``lab_assignments`` is one claim on a combination::

    (no active claim) ──claim──► CLAIMED
    CLAIMED | IN_PROGRESS ──release──► RELEASED    (manual or stale timeout)
    CLAIMED | IN_PROGRESS ──complete─► COMPLETED   (firing log confirmed)

    RELEASED and COMPLETED are terminal.  Re-claiming a combination inserts a
    new row; a closed row is never reopened.

``IN_PROGRESS`` is allowed by the schema and treated as active by every
reader, but no code path writes it today. It is kept so rows already stored
with it keep working.

Stored values are unchanged (``"claimed"``, ``"released"`` ...), so existing
databases read and write exactly as before.
"""

from __future__ import annotations

import sqlite3
from enum import Enum


class ClaimStatus(str, Enum):
    """Status column of ``lab_assignments``."""

    CLAIMED = "claimed"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    RELEASED = "released"


class IllegalClaimTransition(ValueError):
    """Raised when a claim move targets a state it cannot reach."""


ACTIVE_STATUSES: tuple[ClaimStatus, ...] = (
    ClaimStatus.CLAIMED,
    ClaimStatus.IN_PROGRESS,
)
TERMINAL_STATUSES: tuple[ClaimStatus, ...] = (
    ClaimStatus.COMPLETED,
    ClaimStatus.RELEASED,
)
INITIAL_STATUS = ClaimStatus.CLAIMED

#: Legal moves: source states → target state.
TRANSITIONS: dict[str, tuple[tuple[ClaimStatus, ...], ClaimStatus]] = {
    "release": (ACTIVE_STATUSES, ClaimStatus.RELEASED),
    "complete": (ACTIVE_STATUSES, ClaimStatus.COMPLETED),
}


def is_active(status: str | None) -> bool:
    """True for a claim that still holds the combination."""
    return status in {s.value for s in ACTIVE_STATUSES}


def sql_in(statuses: tuple[ClaimStatus, ...]) -> tuple[str, list[str]]:
    """``(placeholders, params)`` for ``status IN (...)`` over ``statuses``."""
    return ", ".join("?" for _ in statuses), [s.value for s in statuses]


def can_transition(source: str | None, move: str) -> bool:
    """Whether ``move`` is legal from a claim currently in ``source``."""
    if move not in TRANSITIONS:
        return False
    sources, _ = TRANSITIONS[move]
    return source in {s.value for s in sources}


def apply(
    cursor: sqlite3.Cursor, move: str, where_sql: str, params: tuple | list
) -> int:
    """Run ``move`` on every matching claim that is in a legal source state.

    ``where_sql`` narrows the rows (e.g. ``"studio_id = ? AND combination_id = ?"``)
    and must not mention ``status``. Returns the number of claims moved.
    """
    if move not in TRANSITIONS:
        raise IllegalClaimTransition(f"Unknown claim transition: {move!r}")
    sources, target = TRANSITIONS[move]
    placeholders, source_params = sql_in(sources)
    # where_sql is a fixed string chosen by callers in this package, never input.
    cursor.execute(
        f"UPDATE lab_assignments SET status = ? "  # nosec B608
        f"WHERE {where_sql} AND status IN ({placeholders})",
        [target.value, *params, *source_params],
    )
    return cursor.rowcount
