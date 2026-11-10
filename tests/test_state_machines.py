"""Tests for the explicit state machines.

Covers the three lifecycles that used to be implicit free-text columns:

* experiments ``stage`` + ``status``   (core/experiments/lifecycle.py)
* lab_assignments ``status``           (core/studios/claims.py)
* combinations ``stage``               (core/combinations/stages.py)

Every test marked "BUG" fails on the code before this refactor.
"""

import json
import sqlite3
from unittest.mock import patch

import pytest
from hypothesis import HealthCheck, settings
from hypothesis import strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from core.combinations import CombinationManager, Combination
from core.combinations import stages
from core.combinations.stages import CombinationStage, FiringOutcome
from core.db import connect_db
from core.experiments import Experiment, ExperimentManager
from core.experiments import lifecycle
from core.experiments.lifecycle import (
    STAGE_ORDER,
    ExperimentState,
    IllegalExperimentTransition,
)
from core.experiments.models import ExperimentStage, ExperimentStatus
from core.studios import StudioManager
from core.studios import claims
from core.studios.claims import ClaimStatus, IllegalClaimTransition

# ===========================================================================
# Experiment lifecycle
# ===========================================================================

ALL_EXP_STATES = [
    ExperimentState(s, t) for s in ExperimentStage for t in ExperimentStatus
]


def _expected_advance(state):
    """Reference model for advance(), written independently of lifecycle.py."""
    if state.status in (ExperimentStatus.COMPLETED, ExperimentStatus.FAILED):
        return None
    if state.stage is ExperimentStage.DOCUMENTATION:
        return (ExperimentStage.DOCUMENTATION, ExperimentStatus.COMPLETED)
    nxt = list(ExperimentStage)[list(ExperimentStage).index(state.stage) + 1]
    return (nxt, ExperimentStatus.IN_PROGRESS)


def _apply(state, updates):
    return ExperimentState(
        ExperimentStage(updates.get("stage", state.stage.value)),
        ExperimentStatus(updates.get("status", state.status.value)),
    )


class TestExperimentLifecycleTable:
    def test_stage_order_is_exhaustive_over_enum(self):
        assert set(STAGE_ORDER) == set(ExperimentStage)
        assert len(STAGE_ORDER) == len(ExperimentStage)

    def test_status_partition_is_exhaustive_over_enum(self):
        assert lifecycle.ACTIVE_STATUSES | lifecycle.TERMINAL_STATUSES == set(
            ExperimentStatus
        )
        assert not lifecycle.ACTIVE_STATUSES & lifecycle.TERMINAL_STATUSES

    @pytest.mark.parametrize("state", ALL_EXP_STATES, ids=str)
    def test_advance_table(self, state):
        expected = _expected_advance(state)
        if expected is None:
            with pytest.raises(IllegalExperimentTransition):
                lifecycle.advance(state)
            return
        updates = lifecycle.advance(state)
        after = _apply(state, updates)
        assert (after.stage, after.status) == expected
        assert ("completed_at" in updates) == (
            expected[1] is ExperimentStatus.COMPLETED
        )

    @pytest.mark.parametrize("state", ALL_EXP_STATES, ids=str)
    def test_fail_table(self, state):
        if state.is_terminal:
            with pytest.raises(IllegalExperimentTransition):
                lifecycle.fail(state)
        else:
            assert lifecycle.fail(state) == {"status": "failed"}

    @pytest.mark.parametrize("state", ALL_EXP_STATES, ids=str)
    def test_start_table(self, state):
        if state.status is ExperimentStatus.PENDING:
            assert lifecycle.start(state) == {"status": "in_progress"}
        else:
            with pytest.raises(IllegalExperimentTransition):
                lifecycle.start(state)

    @pytest.mark.parametrize("state", ALL_EXP_STATES, ids=str)
    def test_complete_table(self, state):
        legal = not state.is_terminal and state.stage is ExperimentStage.DOCUMENTATION
        if legal:
            assert lifecycle.complete(state)["status"] == "completed"
        else:
            with pytest.raises(IllegalExperimentTransition):
                lifecycle.complete(state)

    @pytest.mark.parametrize("target", list(ExperimentStatus))
    def test_transition_for_status_covers_every_status(self, target):
        state = ExperimentState(ExperimentStage.DOCUMENTATION, ExperimentStatus.PENDING)
        if target is ExperimentStatus.PENDING:
            with pytest.raises(IllegalExperimentTransition):
                lifecycle.transition_for_status(state, target.value)
        else:
            updates = lifecycle.transition_for_status(state, target.value)
            assert updates["status"] == target.value

    def test_transition_for_unknown_status_refused(self):
        state = ExperimentState(ExperimentStage.IDEATION, ExperimentStatus.PENDING)
        with pytest.raises(IllegalExperimentTransition):
            lifecycle.transition_for_status(state, "done")

    @pytest.mark.parametrize("stage", list(ExperimentStage))
    @pytest.mark.parametrize("status", list(ExperimentStatus))
    def test_validate_initial(self, stage, status):
        if status in lifecycle.ACTIVE_STATUSES:
            assert lifecycle.validate_initial(stage.value, status.value) == {
                "stage": stage.value,
                "status": status.value,
            }
        else:
            with pytest.raises(IllegalExperimentTransition):
                lifecycle.validate_initial(stage.value, status.value)

    @pytest.mark.parametrize("stage,status", [("bogus", "pending"), ("ideation", "x")])
    def test_validate_initial_rejects_unknown_values(self, stage, status):
        with pytest.raises(IllegalExperimentTransition):
            lifecycle.validate_initial(stage, status)

    def test_legacy_unknown_values_read_tolerantly(self):
        state = ExperimentState.read("legacy-stage", "legacy-status")
        assert state == ExperimentState(
            ExperimentStage.IDEATION, ExperimentStatus.PENDING
        )
        assert lifecycle.stage_index("legacy-stage") == 0
        assert lifecycle.stage_index(None) == 0
        assert Experiment(stage="legacy-stage").stage_order == 0
        assert Experiment(stage="analysis").stage_order == 4


@pytest.fixture
def exp_mgr(test_db_path):
    return ExperimentManager(test_db_path)


def _row(db_path, exp_id):
    conn = connect_db(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM experiments WHERE id = ?", (exp_id,)).fetchone()
    conn.close()
    return dict(row)


class TestExperimentManager:
    def _new(self, mgr, **kw):
        return mgr.create(Experiment(base_glaze="A", top_glaze="B", **kw))

    def test_stored_values_unchanged(self, exp_mgr, test_db_path):
        exp_id = self._new(exp_mgr)
        row = _row(test_db_path, exp_id)
        assert (row["stage"], row["status"]) == ("ideation", "pending")
        exp_mgr.advance_stage(exp_id)
        row = _row(test_db_path, exp_id)
        assert (row["stage"], row["status"]) == ("prediction", "in_progress")

    def test_full_walk_to_completion(self, exp_mgr, test_db_path):
        exp_id = self._new(exp_mgr)
        for _ in range(len(STAGE_ORDER)):
            assert exp_mgr.advance_stage(exp_id)
        row = _row(test_db_path, exp_id)
        assert (row["stage"], row["status"]) == ("documentation", "completed")
        assert row["completed_at"]

    def test_bug_advanced_experiment_shows_as_active(self, exp_mgr):
        """BUG: nothing ever wrote in_progress, so get_active() was always empty."""
        exp_id = self._new(exp_mgr)
        exp_mgr.advance_stage(exp_id)
        assert [e.id for e in exp_mgr.get_active()] == [exp_id]

    def test_bug_failed_experiment_cannot_be_advanced(self, exp_mgr, test_db_path):
        """BUG: advance_stage ignored status, so a failed experiment kept moving
        and at the last stage was flipped to 'completed'."""
        exp_id = self._new(exp_mgr, stage="documentation")
        assert exp_mgr.set_status(exp_id, "failed")
        assert exp_mgr.advance_stage(exp_id) is False
        assert _row(test_db_path, exp_id)["status"] == "failed"

    def test_bug_completed_experiment_keeps_completed_at(self, exp_mgr, test_db_path):
        """BUG: advancing a completed experiment rewrote completed_at each time."""
        exp_id = self._new(exp_mgr, stage="documentation")
        assert exp_mgr.advance_stage(exp_id)
        first = _row(test_db_path, exp_id)["completed_at"]
        assert exp_mgr.advance_stage(exp_id) is False
        assert _row(test_db_path, exp_id)["completed_at"] == first

    def test_bug_create_refuses_already_finished_experiment(self, exp_mgr):
        """BUG: an experiment could be created already 'completed' without a
        completed_at, an illegal state no transition produces."""
        with pytest.raises(ValueError):
            self._new(exp_mgr, status="completed")

    def test_create_unknown_stage_refused(self, exp_mgr):
        with pytest.raises(ValueError):
            self._new(exp_mgr, stage="kiln")

    def test_frontend_firing_log_creation_still_allowed(self, exp_mgr, test_db_path):
        exp_id = self._new(exp_mgr, stage="firing", status="in_progress")
        row = _row(test_db_path, exp_id)
        assert (row["stage"], row["status"]) == ("firing", "in_progress")

    @pytest.mark.parametrize("col", sorted(lifecycle.LIFECYCLE_COLUMNS))
    def test_generic_update_cannot_write_lifecycle_columns(self, exp_mgr, col):
        exp_id = self._new(exp_mgr)
        with pytest.raises(IllegalExperimentTransition):
            exp_mgr.update(exp_id, {col: "completed"})

    def test_generic_update_still_writes_other_columns(self, exp_mgr, test_db_path):
        exp_id = self._new(exp_mgr)
        assert exp_mgr.record_result(exp_id, "glossy", rating=4)
        assert _row(test_db_path, exp_id)["result"] == "glossy"

    def test_set_status_back_to_pending_refused(self, exp_mgr, test_db_path):
        exp_id = self._new(exp_mgr)
        exp_mgr.advance_stage(exp_id)
        assert exp_mgr.set_status(exp_id, "pending") is False
        assert _row(test_db_path, exp_id)["status"] == "in_progress"

    def test_set_status_completed_only_at_last_stage(self, exp_mgr, test_db_path):
        exp_id = self._new(exp_mgr)
        assert exp_mgr.set_status(exp_id, "completed") is False
        assert _row(test_db_path, exp_id)["status"] == "pending"

    def test_missing_experiment(self, exp_mgr):
        assert exp_mgr.advance_stage(9999) is False
        assert exp_mgr.set_status(9999, "failed") is False

    def test_pipeline_stats_cover_every_enum_value(self, exp_mgr):
        stats = exp_mgr.get_pipeline_stats()
        assert set(stats["by_stage"]) == {s.value for s in ExperimentStage}
        assert set(stats["by_status"]) == {s.value for s in ExperimentStatus}


@settings(
    max_examples=40,
    stateful_step_count=25,
    deadline=None,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
)
class ExperimentMachine(RuleBasedStateMachine):
    """Drive random advance / set_status sequences against a real SQLite DB."""

    @initialize(
        stage=st.sampled_from(list(ExperimentStage)),
        status=st.sampled_from(sorted(lifecycle.ACTIVE_STATUSES)),
    )
    def setup(self, stage, status):
        import os
        import tempfile
        from pathlib import Path

        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        conn = connect_db(self.path)
        conn.executescript(
            (Path(__file__).parent.parent / "core" / "schema.sql").read_text()
        )
        conn.commit()
        conn.close()
        self.mgr = ExperimentManager(self.path)
        self.exp_id = self.mgr.create(
            Experiment(base_glaze="A", top_glaze="B", stage=stage, status=status)
        )
        self.model = ExperimentState(stage, status)

    def teardown(self):
        import os

        if getattr(self, "path", None):
            os.unlink(self.path)

    @rule()
    def advance(self):
        expected = _expected_advance(self.model)
        ok = self.mgr.advance_stage(self.exp_id)
        assert ok == (expected is not None)
        if expected:
            self.model = ExperimentState(*expected)

    @rule(wanted=st.sampled_from(list(ExperimentStatus)))
    def set_status(self, wanted):
        target = wanted
        before = self.model
        ok = self.mgr.set_status(self.exp_id, target.value)
        legal = {
            ExperimentStatus.PENDING: False,
            ExperimentStatus.IN_PROGRESS: before.status is ExperimentStatus.PENDING,
            ExperimentStatus.FAILED: not before.is_terminal,
            ExperimentStatus.COMPLETED: not before.is_terminal
            and before.stage is ExperimentStage.DOCUMENTATION,
        }[target]
        assert ok == legal
        if legal:
            self.model = ExperimentState(before.stage, target)

    @invariant()
    def db_matches_model(self):
        if not hasattr(self, "mgr"):
            return
        row = _row(self.path, self.exp_id)
        assert (row["stage"], row["status"]) == (
            self.model.stage.value,
            self.model.status.value,
        )
        # completed_at is set exactly when the experiment is completed
        assert bool(row["completed_at"]) == (
            self.model.status is ExperimentStatus.COMPLETED
        )


TestExperimentMachine = ExperimentMachine.TestCase


# ===========================================================================
# Lab claim lifecycle
# ===========================================================================


class TestClaimTable:
    def test_partition_is_exhaustive_over_enum(self):
        assert set(claims.ACTIVE_STATUSES) | set(claims.TERMINAL_STATUSES) == set(
            ClaimStatus
        )
        assert not set(claims.ACTIVE_STATUSES) & set(claims.TERMINAL_STATUSES)
        assert claims.INITIAL_STATUS in claims.ACTIVE_STATUSES

    @pytest.mark.parametrize("source", list(ClaimStatus))
    @pytest.mark.parametrize("move", sorted(claims.TRANSITIONS))
    def test_transition_table(self, source, move):
        assert claims.can_transition(source.value, move) == (
            source in claims.ACTIVE_STATUSES
        )

    def test_targets_are_terminal(self):
        for _, target in claims.TRANSITIONS.values():
            assert target in claims.TERMINAL_STATUSES

    @pytest.mark.parametrize("status", list(ClaimStatus))
    def test_is_active(self, status):
        assert claims.is_active(status.value) == (status in claims.ACTIVE_STATUSES)

    def test_unknown_values(self):
        assert claims.is_active(None) is False
        assert claims.is_active("bogus") is False
        assert claims.can_transition("claimed", "teleport") is False

    def test_apply_unknown_move_refused(self, test_db_path):
        conn = connect_db(test_db_path)
        with pytest.raises(IllegalClaimTransition):
            claims.apply(conn.cursor(), "teleport", "1 = ?", (1,))
        conn.close()


@pytest.fixture
def studio(test_db_path):
    mgr = StudioManager(test_db_path, user_id="u1")
    studio_id = mgr.create_studio("Lab", "Ana")["id"]
    combo_id = CombinationManager(test_db_path).create(
        Combination(base="X", top="Y", type="user-prediction")
    )
    return mgr, studio_id, combo_id


def _claim_rows(db_path):
    conn = connect_db(db_path)
    rows = conn.execute("SELECT status FROM lab_assignments ORDER BY id").fetchall()
    conn.close()
    return [r[0] for r in rows]


def _queue_entry(mgr, studio_id, combo_id):
    return [c for c in mgr.get_lab_queue(studio_id) if c["id"] == combo_id]


class TestClaimManager:
    def test_claim_release_reclaim(self, studio, test_db_path):
        mgr, sid, cid = studio
        assert mgr.claim_combo(sid, cid, "u1", "Ana").status == "claimed"
        assert mgr.claim_combo(sid, cid, "u2", "Bo") is None  # already held
        assert mgr.release_combo(sid, cid)
        assert mgr.release_combo(sid, cid) is False  # released is terminal
        assert mgr.claim_combo(sid, cid, "u2", "Bo") is not None
        assert _claim_rows(test_db_path) == ["released", "claimed"]

    def test_complete_is_terminal(self, studio, test_db_path):
        mgr, sid, cid = studio
        mgr.claim_combo(sid, cid, "u1", "Ana")
        assert mgr.complete_claim(sid, cid, 1)
        assert mgr.complete_claim(sid, cid, 1) is False
        assert mgr.release_combo(sid, cid) is False
        assert _claim_rows(test_db_path) == ["completed"]

    def test_bug_released_combo_returns_to_queue(self, studio):
        """BUG: the queue filtered la.status after the LEFT JOIN, so a combo
        whose only claim was 'released' vanished from the queue instead of
        going back to the pool."""
        mgr, sid, cid = studio
        assert len(_queue_entry(mgr, sid, cid)) == 1
        mgr.claim_combo(sid, cid, "u1", "Ana")
        [entry] = _queue_entry(mgr, sid, cid)
        assert entry["claim"]["status"] == "claimed"
        mgr.release_combo(sid, cid)
        [entry] = _queue_entry(mgr, sid, cid)
        assert entry["claim"] is None

    def test_completed_combo_leaves_queue(self, studio):
        mgr, sid, cid = studio
        mgr.claim_combo(sid, cid, "u1", "Ana")
        mgr.complete_claim(sid, cid, 1)
        assert _queue_entry(mgr, sid, cid) == []

    def test_released_then_reclaimed_listed_once(self, studio):
        mgr, sid, cid = studio
        mgr.claim_combo(sid, cid, "u1", "Ana")
        mgr.release_combo(sid, cid)
        mgr.claim_combo(sid, cid, "u2", "Bo")
        [entry] = _queue_entry(mgr, sid, cid)
        assert entry["claim"]["assigned_to"] == "u2"

    def test_legacy_in_progress_rows_are_active(self, studio, test_db_path):
        mgr, sid, cid = studio
        conn = connect_db(test_db_path)
        conn.execute(
            "INSERT INTO lab_assignments (studio_id, combination_id, assigned_to,"
            " claimed_at, status) VALUES (?, ?, 'u1', '2026-01-01', 'in_progress')",
            (sid, cid),
        )
        conn.commit()
        conn.close()
        assert mgr.claim_combo(sid, cid, "u2", "Bo") is None
        assert [c.status for c in mgr.get_my_claims(sid, "u1")] == ["in_progress"]
        assert _queue_entry(mgr, sid, cid)[0]["claim"]["status"] == "in_progress"
        assert mgr.complete_claim(sid, cid, 1)

    def test_stale_claims_released(self, studio, test_db_path):
        mgr, sid, cid = studio
        mgr.claim_combo(sid, cid, "u1", "Ana")
        conn = connect_db(test_db_path)
        conn.execute("UPDATE lab_assignments SET claimed_at = '2000-01-01'")
        conn.commit()
        conn.close()
        assert mgr.release_stale_claims() == 1
        assert mgr.release_stale_claims() == 0
        assert _claim_rows(test_db_path) == ["released"]


@settings(
    max_examples=30,
    stateful_step_count=20,
    deadline=None,
)
class ClaimMachine(RuleBasedStateMachine):
    """Random claim / release / complete sequences on one combo."""

    @initialize()
    def setup(self):
        import os
        import tempfile
        from pathlib import Path

        fd, self.path = tempfile.mkstemp(suffix=".db")
        os.close(fd)
        conn = connect_db(self.path)
        conn.executescript(
            (Path(__file__).parent.parent / "core" / "schema.sql").read_text()
        )
        conn.commit()
        conn.close()
        self.mgr = StudioManager(self.path, user_id="u1")
        self.sid = self.mgr.create_studio("Lab", "Ana")["id"]
        self.cid = CombinationManager(self.path).create(
            Combination(base="X", top="Y", type="user-prediction")
        )
        self.held = False
        self.completed = False

    def teardown(self):
        import os

        if getattr(self, "path", None):
            os.unlink(self.path)

    @rule(user=st.sampled_from(["u1", "u2"]))
    def claim(self, user):
        got = self.mgr.claim_combo(self.sid, self.cid, user, user)
        assert (got is not None) == (not self.held)
        if got is not None:
            self.held = True

    @rule()
    def release(self):
        assert self.mgr.release_combo(self.sid, self.cid) == self.held
        self.held = False

    @rule()
    def complete(self):
        assert self.mgr.complete_claim(self.sid, self.cid, 1) == self.held
        if self.held:
            self.completed = True
        self.held = False

    @invariant()
    def at_most_one_active_claim_and_queue_consistent(self):
        if not hasattr(self, "mgr"):
            return
        rows = _claim_rows(self.path)
        active = [s for s in rows if claims.is_active(s)]
        assert len(active) == (1 if self.held else 0)
        assert all(s in {c.value for c in ClaimStatus} for s in rows)
        entries = _queue_entry(self.mgr, self.sid, self.cid)
        if self.completed and not self.held:
            assert entries == []
        elif not self.completed:
            assert len(entries) == 1
            assert (entries[0]["claim"] is not None) == self.held


TestClaimMachine = ClaimMachine.TestCase


# ===========================================================================
# Combination stage
# ===========================================================================


class TestCombinationStageTable:
    @pytest.mark.parametrize("stage", list(CombinationStage))
    def test_every_canonical_stage_writable(self, stage):
        assert stages.validate_stage(stage.value) == stage.value

    @pytest.mark.parametrize("value", ["tested", "proven", "confirmed", "", None, 3])
    def test_unknown_and_legacy_values_not_writable(self, value):
        with pytest.raises(stages.IllegalStageTransition):
            stages.validate_stage(value)

    @pytest.mark.parametrize("stage", list(CombinationStage))
    def test_has_been_fired_table(self, stage):
        assert stages.has_been_fired(stage.value) == (
            stage in (CombinationStage.FIRED, CombinationStage.DOCUMENTED)
        )

    @pytest.mark.parametrize("legacy", sorted(stages.LEGACY_FIRED_STAGES))
    def test_legacy_fired_values_still_read(self, legacy):
        assert stages.has_been_fired(legacy)

    @pytest.mark.parametrize("outcome", list(FiringOutcome))
    def test_outcome_updates(self, outcome):
        assert stages.outcome_updates(outcome.value) == {
            "type": outcome.value,
            "prediction_grade": outcome.value,
            "stage": "documented",
        }
        assert stages.outcome_updates(outcome.value, "r")["result"] == "r"

    def test_unknown_outcome_refused(self):
        with pytest.raises(stages.IllegalStageTransition):
            stages.outcome_updates("proven")


@pytest.fixture
def combo_mgr(test_db_path):
    return CombinationManager(test_db_path)


class TestCombinationManagerStage:
    def test_create_default_and_unknown(self, combo_mgr):
        cid = combo_mgr.create(Combination(base="a", top="b", type="user-prediction"))
        assert combo_mgr.get_by_id(cid).stage == "idea"
        with pytest.raises(ValueError):
            combo_mgr.create(
                Combination(base="a", top="b", type="user-prediction", stage="zzz")
            )

    def test_manual_moves_between_any_canonical_stages(self, combo_mgr):
        cid = combo_mgr.create(Combination(base="a", top="b", type="user-prediction"))
        for target in reversed(list(CombinationStage)):
            assert combo_mgr.update(cid, {"stage": target.value})
            assert combo_mgr.get_by_id(cid).stage == target.value

    def test_update_unknown_stage_refused(self, combo_mgr):
        cid = combo_mgr.create(Combination(base="a", top="b", type="user-prediction"))
        with pytest.raises(ValueError):
            combo_mgr.update(cid, {"stage": "proven"})
        assert combo_mgr.get_by_id(cid).stage == "idea"

    @pytest.mark.parametrize(
        "method,outcome",
        [("promote_to_confirmed", "confirmed"), ("mark_as_surprise", "surprise")],
    )
    def test_outcome_wrappers(self, combo_mgr, method, outcome):
        cid = combo_mgr.create(Combination(base="a", top="b", type="user-prediction"))
        assert getattr(combo_mgr, method)(cid, "nice")
        c = combo_mgr.get_by_id(cid)
        assert (c.stage, c.type, c.prediction_grade, c.result) == (
            "documented",
            outcome,
            outcome,
            "nice",
        )

    def test_bug_progress_counts_documented_combos(self, test_db_path):
        """BUG: /api/progress counted stage IN ('tested','proven','confirmed'),
        values no code writes, so promoted ('documented') combos never counted."""
        mgr = CombinationManager(test_db_path, user_id="u1")
        cid = mgr.create(Combination(base="a", top="b", type="user-prediction"))
        conn = connect_db(test_db_path)
        assert stages.count_fired(conn.cursor(), "u1") == 0
        mgr.promote_to_confirmed(cid, "ok")
        assert stages.count_fired(conn.cursor(), "u1") == 1
        # legacy rows still count
        conn.execute(
            "INSERT INTO combinations (user_id, base, top, type, stage)"
            " VALUES ('u1', 'c', 'd', 'confirmed', 'proven')"
        )
        assert stages.count_fired(conn.cursor(), "u1") == 2
        conn.close()
        # Every outcome transition must land on a stage the counter sees, and
        # the /api/progress route must use this counter rather than its own
        # hard-coded list (the old list missed 'documented').
        for outcome in FiringOutcome:
            assert stages.has_been_fired(stages.outcome_updates(outcome)["stage"])
        import inspect

        import server

        assert "count_fired(cursor, user_id)" in inspect.getsource(server)


# ===========================================================================
# Routes
# ===========================================================================


@pytest.fixture
def client(test_db_path):
    with patch.dict(
        "os.environ",
        {
            "DATABASE_PATH": test_db_path,
            "AI_PROVIDER": "lmstudio",
            "LM_STUDIO_URL": "http://127.0.0.1:1234/v1",
            "LM_STUDIO_MODEL": "test-model",
        },
    ):
        from server import create_app

        app = create_app({"mode": "personal", "database": {"path": test_db_path}})
    return app.test_client()


class TestRoutes:
    def test_create_experiment_illegal_state_is_400(self, client):
        resp = client.post(
            "/api/experiments",
            json={"base_glaze": "A", "top_glaze": "B", "status": "completed"},
        )
        assert resp.status_code == 400

    def test_advance_terminal_experiment_is_400(self, client):
        resp = client.post(
            "/api/experiments",
            json={"base_glaze": "A", "top_glaze": "B", "stage": "documentation"},
        )
        exp_id = json.loads(resp.data)["id"]
        assert client.post(f"/api/experiments/{exp_id}/advance").status_code == 200
        assert client.post(f"/api/experiments/{exp_id}/advance").status_code == 400

    def test_put_unknown_combination_stage_is_400(self, client):
        resp = client.put("/api/combinations/1", json={"stage": "proven"})
        assert resp.status_code == 400

    def test_put_canonical_combination_stage(self, client):
        resp = client.put("/api/combinations/1", json={"stage": "testing"})
        assert resp.status_code == 200

    def test_bug_firing_log_confirmation_documents_combo(self, client, test_db_path):
        """BUG: the firing-log route copied the 'record outcome' transition but
        left out stage='documented', so the two copies disagreed."""
        resp = client.post(
            "/api/experiments",
            json={
                "base_glaze": "Tenmoku",
                "top_glaze": "Chun Blue",
                "combination_id": 1,
                "stage": "firing",
                "status": "in_progress",
            },
        )
        exp_id = json.loads(resp.data)["id"]
        resp = client.post(
            f"/api/experiments/{exp_id}/firing-log",
            json={
                "clay_body": "stoneware",
                "firing_type": "reduction",
                "cone": "10",
                "confirmation": "confirmed",
            },
        )
        assert resp.status_code == 200
        c = CombinationManager(test_db_path).get_by_id(1)
        assert (c.stage, c.type, c.prediction_grade) == (
            "documented",
            "confirmed",
            "confirmed",
        )
