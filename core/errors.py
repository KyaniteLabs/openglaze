"""Agent-facing error payloads with concrete retry invocations.

Equivalent of kinocut's ``errors.py::retry_message``: every error code maps
to a concrete re-invocation an agent (MCP client, CLI user, or HTTP caller)
can execute immediately — an error message must never dead-end the caller.
"""

from __future__ import annotations

# Error code → concrete re-invocation. Surfaces are listed in the order
# MCP, CLI, HTTP because agents hit the MCP server first.
_RETRY_INVOCATIONS = {
    "missing_recipe": (
        'analyze_glaze_recipe with recipe="Custer Feldspar 45, Silica 25, Whiting 18, EPK 12" '
        '(MCP) / openglaze_cli umf --recipe "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12" (CLI) / '
        "POST /api/chemistry/optimize with a recipe field (HTTP)"
    ),
    "missing_batch_size": (
        "scale_glaze_batch with size=300 (MCP) / openglaze_cli batch --recipe '...' --size 300 (CLI) / "
        "POST /api/chemistry/scale with batch_size_grams (HTTP)"
    ),
    "invalid_size": (
        "scale_glaze_batch with a positive size, e.g. size=300 (MCP) / openglaze_cli batch --size 300 (CLI)"
    ),
    "invalid_target": (
        'POST /api/chemistry/optimize with target one of target_cte, reduce_cte, increase_cte, '
        "more_matte, more_glossy, reduce_alkali, reduce_running (HTTP)"
    ),
    "missing_target_value": (
        "POST /api/chemistry/optimize with target=target_cte and target_value=6.5 (HTTP)"
    ),
    "glaze_not_found": (
        "GET /api/glazes to list names, then GET /api/glazes/<name-or-id>/umf (HTTP)"
    ),
    "combination_not_found": (
        "GET /api/combinations to list ids, then GET /api/combinations/<id> (HTTP)"
    ),
    "experiment_not_found": (
        "GET /api/experiments to list ids, then POST /api/experiments/<id>/advance (HTTP)"
    ),
    "auth_required": (
        "POST /api/auth/simple-login with display_name to get a token, then retry the write (HTTP)"
    ),
    "rate_limited": (
        "the same request after waiting retry_after seconds (respect the Retry-After header)"
    ),
    "not_found": ("GET /api/health to confirm the server, then GET /api/glazes for live routes (HTTP)"),
    "chemistry_unavailable": (
        "analyze_glaze_recipe with the same recipe (MCP) / openglaze_cli umf --recipe '...' (CLI) — "
        "the offline chemistry engine is importable on every surface"
    ),
    "server_error": ("the same request after checking GET /api/health (HTTP)"),
}

_DEFAULT_INVOCATION = "the same call with corrected parameters (MCP / CLI / HTTP)"


def retry_invocation(code: str) -> str:
    """Return the concrete re-invocation for an error code."""
    return _RETRY_INVOCATIONS.get(code, _DEFAULT_INVOCATION)


def retry_message(message: str, code: str) -> str:
    """Append a concrete retry invocation to an error message (kinocut pattern)."""
    return f"{message}; retry with {retry_invocation(code)}"


def error_payload(text: str, code: str, **extra) -> dict:
    """Build an agent-facing error JSON body with a retry hint.

    The ``retry`` field carries the machine-readable invocation; the message
    itself ends with the same hint so single-field consumers still see it.
    """
    payload = {
        "error": retry_message(text, code),
        "code": code,
        "retry": retry_invocation(code),
    }
    payload.update(extra)
    return payload
