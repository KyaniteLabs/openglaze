# OpenGlaze architecture

OpenGlaze is a self-hosted ceramic recipe notebook and chemistry calculator.
This map describes the current source, not the server split proposed in PR #175.
Engineering owns implementation layers; Product owns product descriptions.

## Parts and one data flow

- `frontend/index.html`, `frontend/scripts/` and `frontend/styles/` implement the
  no-build browser UI; `frontend/sw.js` implements its service worker.
- `server.py` creates the Flask app, registers API/static routes, initializes and
  seeds SQLite, and constructs request-scoped managers.
- `core/glazes/`, `core/combinations/`, `core/experiments/` and `core/studios/`
  implement notebook persistence; `core/gamification/` and `core/predictions/`
  implement optional participation features.
- `core/chemistry/` calculates UMF, estimated expansion, substitutions, batches,
  compatibility and optimization. `core/chemistry/data_loader.py` reads
  `ceramics-foundation/data/` and modules have fallback data.
- `core/ai/context.py` retrieves notebook/reference context;
  `core/ai/kama.py` sends it to a configured model provider and streams answers.
- `openglaze_cli.py`, `openglaze_mcp.py` and `skills/openglaze/SKILL.md` expose
  local agent workflows. `docs/` is a separate public discovery/documentation site.

Example: a browser posts a recipe to `/api/glazes`; `server.py` applies the
mode-dependent write-auth check and delegates to `GlazeManager`. The manager
writes SQLite through `core/db.py`; subsequent glaze/chemistry requests return
stored recipe information and calculated analysis to the browser. CLI/MCP
chemistry calculations also operate without a running HTTP server.

## Trust and persistence

`config/` selects personal/cloud behavior. Personal mode is not a multi-tenant
security boundary. `core/auth/` contains simple process-local bearer sessions
and experimental Kratos integration; `core/security/` provides request controls.
Review actual route authorization before exposing an installation publicly.

SQLite (`core/schema.sql`, `core/db.py`) and uploaded local files
(`core/upload_utils.py`) are durable state. `docker-compose.yml` persists database
and upload volumes; PostgreSQL configuration is not a PostgreSQL-backed manager
implementation. Simple sessions, rate limiting and AI conversation history are
process-local and disappear on restart. Optional AI calls cross a network and
can disclose supplied recipe/context/image data; self-hosting alone does not
make configured cloud inference private.

## Risk, failure and verification

Schema/manager changes risk data loss or ownership mistakes; auth/config/upload
changes risk exposure. Chemistry coefficients, units and reference-data changes
can silently alter recommendations: predictions are not fired-test or food-safety
certification. AI endpoint/prompt changes affect disclosure and reliability.
SQLite contention, missing data and model timeouts are observable in logs/API
responses; some glaze-read database errors return an empty list. `/health` is
liveness, not proof of database/model readiness.

Run `pytest tests/`, `black --check .`, and `ruff check .` with
`requirements-dev.txt`. Tests cover chemistry, API CRUD, launch and agent
contracts. `tests/e2e/openglaze-ui-smoke.spec.js` supplies browser smoke coverage.
`.github/workflows/ci.yml` runs Python 3.12–3.14 tests; container smoke is
push-only. `.forgejo/workflows/ci.yml` now fails closed on dependency/lint/test
errors and requires Python 3.12+. See
`qa/FOUNDATION-GAPS.md` for executed results and unresolved remediation; neither
file presence nor a GitHub PR proves mirror adoption.
