"""Agent-facing error payloads with concrete, runnable retry invocations.

Equivalent of kinocut's ``errors.py::retry_message``: every error code maps
to a re-invocation an agent (MCP client, CLI user, or HTTP caller) can
execute immediately — an error message must never dead-end the caller.

Every hint is runnable end-to-end:

* CLI hints use the documented launcher ``python -m openglaze_cli`` (no
  console script is installed) and repeat every required argument, echoing
  the caller's own recipe whenever the recipe itself was valid.
* HTTP hints name the route and carry a complete example body that the
  route accepts as-is.
* Builders take the failed call's context (recipe, size, method, path,
  measured ``retry_after``) so hints preserve the caller's arguments
  instead of guessing.
"""

from __future__ import annotations

from typing import Any, Callable

# Canonical worked example: a parseable four-material recipe used whenever
# the caller's own recipe is unknown or was itself the problem.
EXAMPLE_RECIPE = "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12"

_DEFAULT_INVOCATION = "the same call with corrected parameters (MCP / CLI / HTTP)"


def _recipe_or_example(recipe: str | None) -> str:
    return recipe or EXAMPLE_RECIPE


def _missing_recipe(recipe: str | None = None) -> str:
    r = _recipe_or_example(recipe)
    http_body = f'{{"recipe": "{r}", "target": "increase_cte"}}'
    return (
        f'analyze_glaze_recipe with recipe="{r}" (MCP) / '
        f'python -m openglaze_cli umf --recipe "{r}" (CLI) / '
        f"POST /api/chemistry/optimize with {http_body} (HTTP)"
    )


def _batch_hint(recipe: str | None = None) -> str:
    r = _recipe_or_example(recipe)
    http_body = f'{{"recipe": "{r}", "batch_size_grams": 300}}'
    return (
        f'scale_glaze_batch with recipe="{r}" and size=300 (MCP) / '
        f'python -m openglaze_cli batch --recipe "{r}" --size 300 (CLI) / '
        f"POST /api/chemistry/scale with {http_body} (HTTP)"
    )


def _invalid_cone(recipe: str | None = None) -> str:
    r = _recipe_or_example(recipe)
    return (
        "analyze_glaze_recipe with cone=10 or a zero-padded string like '04' "
        f'(MCP) / python -m openglaze_cli umf --recipe "{r}" --cone 10 (CLI)'
    )


def _unparseable_recipe() -> str:
    # The recipe itself was the problem — hint the canonical example, not
    # the string that just failed to parse.
    r = EXAMPLE_RECIPE
    return (
        f'analyze_glaze_recipe with "<material> <amount>" pairs, e.g. recipe="{r}" (MCP) / '
        f'python -m openglaze_cli umf --recipe "{r}" (CLI)'
    )


def _invalid_target(recipe: str | None = None) -> str:
    r = _recipe_or_example(recipe)
    http_body = f'{{"recipe": "{r}", "target": "increase_cte"}}'
    return (
        f"POST /api/chemistry/optimize with {http_body} — target one of "
        "target_cte, reduce_cte, increase_cte, more_matte, more_glossy, "
        "reduce_alkali, reduce_running (HTTP)"
    )


def _missing_target_value(recipe: str | None = None) -> str:
    r = _recipe_or_example(recipe)
    http_body = f'{{"recipe": "{r}", "target": "target_cte", "target_value": 6.5}}'
    return f"POST /api/chemistry/optimize with {http_body} (HTTP)"


def _rate_limited(
    method: str = "GET", path: str = "/api/health", retry_after: int = 60
) -> str:
    return (
        f"{method} {path} again with the same arguments after {retry_after} seconds — "
        "the measured window in retry_after / the Retry-After header (HTTP)"
    )


# Error code → hint builder. Builders accept keyword context from the failed
# call (recipe, size, method, path, retry_after, ...). Surfaces are listed
# in the order MCP, CLI, HTTP because agents hit the MCP server first.
_RETRY_BUILDERS: dict[str, Callable[..., str]] = {
    "missing_recipe": _missing_recipe,
    "missing_batch_size": _batch_hint,
    "invalid_size": _batch_hint,
    "invalid_cone": _invalid_cone,
    "unparseable_recipe": _unparseable_recipe,
    "invalid_target": _invalid_target,
    "missing_target_value": _missing_target_value,
    "glaze_not_found": lambda: "GET /api/glazes to list names, then GET /api/glazes/<name-or-id>/umf (HTTP)",
    "combination_not_found": lambda: "GET /api/combinations to list ids, then GET /api/combinations/<id> (HTTP)",
    "experiment_not_found": lambda: "GET /api/experiments to list ids, then POST /api/experiments/<id>/advance (HTTP)",
    "auth_required": lambda: (
        "POST /api/auth/simple-login with display_name to get a token, then retry the write (HTTP)"
    ),
    # The denial lane sends the legacy wire code "RATE_LIMITED"; both keys
    # build the same measured, request-specific hint.
    "rate_limited": _rate_limited,
    "RATE_LIMITED": _rate_limited,
    "not_found": lambda: "GET /api/health to confirm the server, then GET /api/glazes for live routes (HTTP)",
    "chemistry_unavailable": lambda: (
        f'analyze_glaze_recipe with recipe="{EXAMPLE_RECIPE}" (MCP) / '
        f'python -m openglaze_cli umf --recipe "{EXAMPLE_RECIPE}" (CLI) — '
        "the offline chemistry engine is importable on every surface"
    ),
    "server_error": lambda: "the same request after checking GET /api/health (HTTP)",
}


def retry_invocation(code: str, **context: Any) -> str:
    """Return the concrete re-invocation for an error code."""
    builder = _RETRY_BUILDERS.get(code)
    if builder is None:
        return _DEFAULT_INVOCATION
    return builder(**context)


def retry_message(message: str, code: str, **context: Any) -> str:
    """Append a concrete retry invocation to an error message (kinocut pattern)."""
    return f"{message}; retry with {retry_invocation(code, **context)}"


def error_payload(
    text: str, code: str, context: dict[str, Any] | None = None, **extra: Any
) -> dict:
    """Build an agent-facing error JSON body with a retry hint.

    The ``retry`` field carries the machine-readable invocation; the message
    itself ends with the same hint so single-field consumers still see it.
    ``context`` carries the failed call's arguments (recipe, method, path,
    measured retry_after, ...) so the hint preserves them.
    """
    invocation = retry_invocation(code, **(context or {}))
    payload = {
        "error": f"{text}; retry with {invocation}",
        "code": code,
        "retry": invocation,
    }
    payload.update(extra)
    return payload
