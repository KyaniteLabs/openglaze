"""Database bootstrap: schema, migrations, and seed data."""

import json
import logging
import sqlite3
from pathlib import Path

from webapp import REPO_ROOT

logger = logging.getLogger(__name__)

# Keep a reference to in-memory DB connections so they don't get garbage-collected
_memory_db_connections: dict = {}


def init_db(db_path: str):
    """Initialize database with schema and seed data."""
    from core.db import connect_db

    conn = connect_db(db_path)
    cursor = conn.cursor()

    schema_path = REPO_ROOT / "core" / "schema.sql"
    if schema_path.exists():
        with open(schema_path, "r") as f:
            cursor.executescript(f.read())
            conn.commit()

    # Run migrations for existing databases
    _run_migrations(conn)

    # Release stale lab claims
    try:
        from core.studios import StudioManager

        studio_mgr = StudioManager(db_path)
        studio_mgr.release_stale_claims()
    except Exception as e:
        logger.debug(f"Lab claim cleanup skipped: {e}")

    # Seed database with glazes and combinations
    seed_database(conn)
    if db_path == ":memory:":
        # Keep connection alive so the in-memory database persists
        _memory_db_connections["main"] = conn
    else:
        conn.close()


def _run_migrations(conn):
    """Run database migrations for existing databases."""
    cursor = conn.cursor()

    # Check if combinations table exists
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='combinations'"
    )
    if not cursor.fetchone():
        return

    # Migration 1: Rename type values
    try:
        cursor.execute(
            "UPDATE combinations SET type = 'research-backed' WHERE type = 'proven'"
        )
        cursor.execute(
            "UPDATE combinations SET type = 'user-prediction' WHERE type = 'hypothesis'"
        )
    except sqlite3.OperationalError:
        pass

    # Migration 2: Add stage column if missing
    cursor.execute("PRAGMA table_info(combinations)")
    columns = [row[1] for row in cursor.fetchall()]
    if "stage" not in columns:
        cursor.execute("ALTER TABLE combinations ADD COLUMN stage TEXT DEFAULT 'idea'")
        # Backfill: research-backed → documented, user-prediction → idea
        cursor.execute(
            "UPDATE combinations SET stage = 'documented' WHERE type = 'research-backed' AND stage = 'idea'"
        )

    # Migration 3: Add prediction_grade column if missing
    if "prediction_grade" not in columns:
        cursor.execute(
            "ALTER TABLE combinations ADD COLUMN prediction_grade TEXT DEFAULT 'unknown'"
        )

    # Migration 4: Add firing log columns to experiments
    _migrate_firing_log_columns(cursor)

    conn.commit()
    logger.info("Database migrations completed")


def _migrate_firing_log_columns(cursor):
    """Add firing-log columns to experiments for older databases."""
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='experiments'"
    )
    if not cursor.fetchone():
        return
    cursor.execute("PRAGMA table_info(experiments)")
    exp_columns = [row[1] for row in cursor.fetchall()]
    firing_cols = {
        "clay_body": "TEXT",
        "firing_type": "TEXT",
        "cone": "TEXT",
        "application_method": "TEXT",
        "thickness": "TEXT",
        "drying_time": "TEXT",
        "cooling_notes": "TEXT",
        "atmosphere_notes": "TEXT",
        "confirmation": "TEXT",
        "fired_by": "TEXT",
        "fired_at": "TIMESTAMP",
        "studio_id": "TEXT",
    }
    for col_name, col_type in firing_cols.items():
        if col_name not in exp_columns:
            cursor.execute(f"ALTER TABLE experiments ADD COLUMN {col_name} {col_type}")


def _load_seed_rules():
    """Load chemistry rules from ceramics-foundation/data/seed-chemistry-rules.json."""
    seed_path = REPO_ROOT / "ceramics-foundation" / "data" / "seed-chemistry-rules.json"
    if not seed_path.exists():
        logger.warning(f"Seed rules not found: {seed_path}")
        return []
    try:
        with open(seed_path) as f:
            data = json.load(f)
        rules = data.get("rules", [])
        return [
            (
                r.get("category", ""),
                r.get("subcategory", ""),
                r.get("name", ""),
                r.get("description", ""),
                r.get("conditions", ""),
                r.get("outcome", ""),
                r.get("caveat", ""),
                r.get("confidence", "medium"),
            )
            for r in rules
        ]
    except (json.JSONDecodeError, OSError) as e:
        logger.error(f"Failed to load seed rules: {e}")
        return []


def _rule_tuple(rule: dict) -> tuple:
    return (
        rule.get("category", ""),
        rule.get("subcategory", ""),
        rule.get("name", ""),
        rule.get("description", ""),
        rule.get("conditions", ""),
        rule.get("outcome", ""),
        rule.get("caveat", ""),
        rule.get("confidence", "medium"),
    )


def _merge_chemistry_rules() -> list:
    """Combine seed rules with external chemistry-rules.json (external wins)."""
    chemistry_rules = _load_seed_rules()
    try:
        from core.chemistry.data_loader import load_chemistry_rules

        external_rules = load_chemistry_rules()
        if external_rules:
            external_tuples = [_rule_tuple(r) for r in external_rules]
            external_keys = {(r[0], r[1], r[2]) for r in external_tuples}
            chemistry_rules = external_tuples + [
                r for r in chemistry_rules if (r[0], r[1], r[2]) not in external_keys
            ]
            logger.info(
                f"Loaded {len(external_tuples)} external rules, "
                f"{len(chemistry_rules) - len(external_tuples)} from seed"
            )
    except ImportError:
        logger.debug("External data_loader not available, using seed rules only")
    return chemistry_rules


def _insert_glazes(cursor, template):
    """Insert community glazes from the YAML template."""
    for glaze in template.get("glazes", []):
        cursor.execute(
            """INSERT OR IGNORE INTO glazes
            (id, name, family, hex, chemistry, behavior, layering, warning, recipe, catalog_code, food_safe, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                glaze.get("id"),
                glaze.get("name"),
                glaze.get("family"),
                glaze.get("hex"),
                glaze.get("chemistry"),
                glaze.get("behavior"),
                glaze.get("layering"),
                glaze.get("warning"),
                glaze.get("recipe"),
                glaze.get("catalog_code"),
                glaze.get("food_safe"),
                glaze.get("notes"),
            ),
        )


def _insert_combination(cursor, combo: dict, combo_type: str, stage: str):
    """Insert one combination row with its layers JSON."""
    layers_json = json.dumps([combo.get("base"), combo.get("top")])
    cursor.execute(
        """INSERT INTO combinations (base, top, layers, type, source, result, chemistry, risk, stage, prediction_grade)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (
            combo.get("base"),
            combo.get("top"),
            layers_json,
            combo_type,
            combo.get("source"),
            combo.get("result"),
            combo.get("chemistry"),
            combo.get("risk"),
            stage,
            combo.get("prediction_grade", "unknown"),
        ),
    )


def seed_database(conn):
    """Seed database with community glazes and combinations if empty."""
    cursor = conn.cursor()

    # Only seed if glazes table is empty
    cursor.execute("SELECT COUNT(*) FROM glazes")
    if cursor.fetchone()[0] > 0:
        return

    logger.info("Seeding database with community glazes and combinations...")

    # Load YAML template
    from core.templates import get_community_glazes

    template = get_community_glazes()
    if not template:
        logger.warning("No template found — skipping seed")
        return

    _insert_glazes(cursor, template)
    for c in template.get("research_backed_combinations", []):
        _insert_combination(cursor, c, "research-backed", "documented")
    for c in template.get("user_prediction_combinations", []):
        _insert_combination(cursor, c, "user-prediction", "idea")

    for rule in _merge_chemistry_rules():
        cursor.execute(
            """INSERT INTO chemistry_rules
            (category, rule_type, title, description, conditions, outcomes, caveats, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            rule,
        )

    conn.commit()
    logger.info("Database seeded successfully")


def get_db_connection(db_path: str) -> sqlite3.Connection:
    """Get database connection."""
    from core.db import connect_db

    conn = connect_db(db_path)
    conn.row_factory = sqlite3.Row
    return conn
