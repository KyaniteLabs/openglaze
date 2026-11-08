# OpenGlaze product

OpenGlaze helps potters, educators and studios keep a self-hosted glaze notebook
and reason about recipes before firing real test tiles. The core experience is
entering/storing a recipe, inspecting its chemistry, adjusting a batch, and
recording experiments and photographs—not buying a hosted recipe community.

## What exists

- Browser/PWA notebook: glaze records, layering combinations, experiment stages,
  firing logs and photo surfaces (`frontend/`, routes in `server.py`,
  `core/glazes/`, `core/combinations/`, `core/experiments/`).
- Chemistry tools: UMF, estimated thermal expansion, batch scaling/cost,
  comparisons, substitutions, defect heuristics and computational optimization
  (`core/chemistry/`). These are estimates, not measured firing outcomes or
  certification that a glaze is food safe.
- Optional Kama consultation: retrieves notebook/reference context and streams
  model responses (`core/ai/`, `config/kama-system-prompt.txt`). Providers include
  local and cloud endpoints; users must consider what context leaves their host.
- Studio/invite, lab queue, points, streaks, badges and prediction surfaces
  (`core/studios/`, `core/gamification/`, `core/predictions/`). Simple login is
  lightweight process-local identity, not durable enterprise authorization.
- Local CLI and stdio MCP chemistry workflows (`openglaze_cli.py`,
  `openglaze_mcp.py`, `skills/openglaze/SKILL.md`).
- Public project/discovery pages in `docs/`; they are not a hosted notebook.

## Reference inputs and limits

Checked-in `ceramics-foundation/data/` contains materials, oxides, clay bodies,
colorants, firing schedules/cones, thermal-expansion coefficients, UMF targets,
layering/substitution rules and safety reference files. Community recipe inputs
include `cone10-reduction-community.yaml`, `cone6-oxidation-community.yaml` and
`core/templates/community-glazes.yaml`; studio examples live in
`ceramics-foundation/recipes/studio/`. Availability in source does not mean every
file is used by every workflow. `core/chemistry/data_loader.py` documents loading
and fallback behavior. Preserve source attribution and applicable content terms;
see `LICENSE`, `README.md` and dataset provenance before redistributing inputs.

Default deployment is personal SQLite plus local uploads. PostgreSQL-backed
managers, durable sessions and stronger collaboration authorization are not
implemented promises (`docs/architecture.md`, `core/db.py`, `core/auth/`).
Glazy/INSIGHT import and broader future work remain roadmap items, not current
capabilities (`ROADMAP.md`). Always validate predictions with physical tests.
