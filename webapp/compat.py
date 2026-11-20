"""Compatibility checker helpers (name-based glaze pair scoring)."""

from webapp.db import get_db_connection


def compute_compatibility(
    glaze_a_name: str, glaze_b_name: str, db_path: str = None
) -> dict:
    """Compute compatibility score between two glazes by name.

    Strategy: DB lookup → property-based scoring → string heuristic fallback.
    """
    # Try DB lookup first
    if db_path:
        conn = get_db_connection(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM glazes WHERE name = ? LIMIT 1", (glaze_a_name,))
        row_a = cursor.fetchone()
        cursor.execute("SELECT * FROM glazes WHERE name = ? LIMIT 1", (glaze_b_name,))
        row_b = cursor.fetchone()
        conn.close()

        if row_a and row_b:
            return compute_compatibility_from_properties(
                dict(row_a), dict(row_b), glaze_a_name, glaze_b_name
            )

    # String heuristic fallback
    return _compute_compatibility_string_matching(glaze_a_name, glaze_b_name)


def compute_compatibility_from_properties(
    glaze_a: dict, glaze_b: dict, name_a: str, name_b: str
) -> dict:
    """Score compatibility based on glaze properties."""
    score = 70  # Base score
    factors = []

    # Check layering hints
    layering_a = glaze_a.get("layering", "") or ""
    layering_b = glaze_b.get("layering", "") or ""
    if layering_a and layering_b:
        score += 5
        factors.append("Both glazes have layering information")

    # Check for Shino warning
    family_a = (glaze_a.get("family", "") or "").lower()
    family_b = (glaze_b.get("family", "") or "").lower()
    name_lower_a = name_a.lower()
    name_lower_b = name_b.lower()

    is_shino_a = "shino" in family_a or "shino" in name_lower_a
    is_shino_b = "shino" in family_b or "shino" in name_lower_b

    if is_shino_a != is_shino_b:
        score -= 15
        factors.append(
            "Shino over non-Shino: moderate crawling risk (thin application recommended)"
        )
    elif is_shino_a and is_shino_b:
        score += 5
        factors.append("Both glazes are Shino — similar chemistry expected")

    # Check for iron overload
    chemistry_a = (glaze_a.get("chemistry", "") or "").lower()
    chemistry_b = (glaze_b.get("chemistry", "") or "").lower()
    if "iron" in chemistry_a and "iron" in chemistry_b:
        score -= 10
        factors.append("Both glazes are iron-rich — may produce very dark results")

    # Check food safety compatibility
    food_safe_a = glaze_a.get("food_safe", "")
    food_safe_b = glaze_b.get("food_safe", "")
    if food_safe_a and food_safe_b:
        if food_safe_a.lower() in ("yes", "true") and food_safe_b.lower() in (
            "yes",
            "true",
        ):
            factors.append("Both glazes are food-safe")

    # Check warnings
    warning_a = glaze_a.get("warning", "") or ""
    warning_b = glaze_b.get("warning", "") or ""
    if warning_a:
        factors.append(f"Warning ({name_a}): {warning_a}")
    if warning_b:
        factors.append(f"Warning ({name_b}): {warning_b}")

    score = max(0, min(100, score))

    verdict = _score_verdict(score)

    return {
        "glaze_a": name_a,
        "glaze_b": name_b,
        "score": score,
        "verdict": verdict,
        "factors": factors,
        "method": "property-based",
    }


def _compute_compatibility_string_matching(glaze_a: str, glaze_b: str) -> dict:
    """Heuristic fallback when DB glazes are not found."""
    score = 65  # Neutral baseline
    factors = ["No database records found — using heuristic matching"]

    name_a = glaze_a.lower()
    name_b = glaze_b.lower()

    # Shino check
    is_shino_a = "shino" in name_a
    is_shino_b = "shino" in name_b
    if is_shino_a != is_shino_b:
        score -= 15
        factors.append("Shino over non-Shino: moderate crawling risk")
    elif is_shino_a and is_shino_b:
        score += 5

    # Clear glaze bonus
    if "clear" in name_a or "clear" in name_b:
        score += 10
        factors.append("Clear glaze — generally compatible with most bases")

    # Iron overload heuristic
    if "iron" in name_a and "iron" in name_b:
        score -= 10
        factors.append("Both appear iron-rich — may produce very dark results")

    score = max(0, min(100, score))

    verdict = _score_verdict(score)

    return {
        "glaze_a": glaze_a,
        "glaze_b": glaze_b,
        "score": score,
        "verdict": verdict,
        "factors": factors,
        "method": "string-heuristic",
    }


def _score_verdict(score: int) -> str:
    """Map a 0-100 compatibility score to a human verdict."""
    if score >= 80:
        return "Excellent match"
    if score >= 60:
        return "Good compatibility"
    if score >= 40:
        return "Use with caution"
    return "High risk — test first"
