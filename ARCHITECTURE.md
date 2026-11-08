# OpenGlaze architecture

## Parts and flow

```text
frontend/ vanilla SPA -> server.py Flask REST/SSE -> mode + SQLite / studio assets
recipe -> core/chemistry parser -> bundled foundation data -> UMF/prediction/compatibility
CLI / stdio MCP ------------------------------------^ (no web server required)
Kama request -> conversation/retrieval/context -> selected model endpoint -> streamed answer
```

[server.py](server.py) assembles configuration, personal/cloud mode, rate/security headers, database initialization/seed data and routes. Its module-level app is lazy; direct execution calls `create_app` and binds the configured address. [core/db.py](core/db.py) scopes connections and SQLite WAL/busy timeout. [frontend](frontend/index.html) loads separate scripts/components; the browser is a consumer of real studio APIs, not the source of record.

[core/chemistry/data_loader.py](core/chemistry/data_loader.py) caches JSON material/oxide/rule/reference tables from `ceramics-foundation/data`, filters metadata keys and exposes deep-copy reads. [UMF](core/chemistry/umf.py) parses ingredient percentages, totals oxide weights, converts to moles and normalizes flux unity before deriving ratios, surface and CTE estimates. Missing materials/warnings remain part of the result. [openglaze_cli.py](openglaze_cli.py) and [openglaze_mcp.py](openglaze_mcp.py) wrap this same local library.

[core/ai/kama.py](core/ai/kama.py) owns conversations, prompt/retrieval context and network provider adapters; it is not needed for deterministic chemistry. Config/environment can select local or remote-compatible services. Constructor and personal-config defaults differ; inspect effective provider, endpoint and model rather than promising offline behavior.

## Risky paths / recognizable failures

- Opening the app creates/seeds its configured database; use an explicit new database for probes, never an existing studio by accident. Upload/photo/database and cloud authentication paths need separate backup/privacy/access review.
- Personal mode has no authentication: keep its bind private. Flask health/chemistry success does not prove cloud tenant isolation, billing, production transport or rate-limit deployment behavior.
- Provider requests may send recipe/conversation context off-host and incur spend. Timeout/fallback output must not become scientific confidence. No model was launched or queried for this docs work.
- Heuristic chemistry depends on material matching, composition and reference quality; missing ingredients, absent flux, unknown firing context or estimated coefficients weaken conclusions. Risk labels are not food-safety or kiln certification.
- Frontend DOMPurify is CDN-loaded; unavailable assets/network change browser behavior. JSON reference data and placeholder studio templates have different validation status.

## Bounded verification

Read README, architecture, config, server/DB, CLI/MCP, data loader, UMF and AI adapter source. A fresh preserved synthetic SQLite studio rendered in Chromium, with `/api/ask` blocked; evidence lives in the session's `evidence/openglaze/`. Pure chemistry suite: 54 passed. CLI recipe calculation passed. No AI, real user data, cloud login, publication or deployment. Independent review, real firing/operator evidence and scientific acceptance remain separate. Rollback: revert these docs; runtime unchanged.
