# Changelog

All notable changes to OpenGlaze will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed
- Docker install on a fresh clone: `cp .env.example .env && docker compose up -d` now reaches a healthy app. Previously postgres exited on boot twice over — a blank `POSTGRES_PASSWORD` (shipped commented) and the Renovate bump to `postgres:18-alpine`, whose images reject the legacy `/var/lib/postgresql/data` mount. `.env.example` now ships a working `POSTGRES_PASSWORD` default, compose interpolations carry inline defaults, and postgres is pinned to `16-alpine` (re-pin together with the volume change). Kratos also crash-looped on v26: the removed `--watch-courier-templates` flag is dropped, and `kratos/config.yml` now validates against the v26 schema (`in: header` on the webhook api_key auth; no `enabled` key on the error flow). The manual SQLite path is unchanged.

## [1.1.0] - 2026-04-27

### Added
- 44 community glazes across cone 6 and 10 (was 32 cone-10-only)
- Cone 6 oxidation glazes for electric kiln users (12 glazes)
- Cone 6 reduction glazes for gas kiln users (4 glazes)
- `cone` and `atmosphere` fields on every glaze entry
- Cone 5-6 layering combinations for the largest potter demographic
- SEO landing pages for calculator, UMF, CTE, and comparison queries
- AI discoverability files (llms.txt, llms-full.txt, ai.txt)
- GitHub Dependabot for automated dependency updates
- E2E smoke test scaffold with Playwright
- Launch contract tests for Docker, CI, and docs consistency
- SEO contract tests for sitemap, landing pages, and AI files
- nginx and nginx-tls reverse proxy configs for self-hosting
- requirements-dev.txt for development dependencies
- CITATION.cff for academic citation support
- ROADMAP.md for project direction visibility

### Changed
- Removed all studio-invented and commercial-product glazes to eliminate IP risk
- Replaced with safe traditional/published/ancient glazes (Song Dynasty, John Britt, etc.)
- Seed data and server templates updated from "studio" to "community" terminology
- Docker Compose uses env var substitution for secrets (no hardcoded passwords)
- CI upgraded: actions/checkout@v6, setup-python@v6, cache@v5, codecov@v6
- Dependencies updated to minimum floors in requirements.txt
- Test suite expanded from 111 to 139 tests
- Live site served from openglaze.kyanitelabs.tech
- `.env.example` cleaned up with proper sections and no default secrets

### Fixed
- Auth enforcement hardened with trusted proxy middleware
- Black and Ruff formatting consistency across codebase
- Duplicate and unused imports removed
- CONTRIBUTING.md port number corrected (8767 → 8768)
- Security headers (CSP, HSTS, X-Frame-Options) enforced
- DOMPurify XSS sanitization on all user content rendering
- SQLite WAL mode enabled for concurrent read/write safety

### Removed
- 7 studio-invented glazes (Clay on First / Default Studio IP)
- Studio-specific data (profile.json, clays.json, kilns.json) archived
- GITHUB_GUARDIAN_AUDIT.md (false-positive noise)
- HANDOFF.md (internal artifact, not user-facing)
- Clay on First / Default Studio references across all docs and code

## [1.0.0] - 2026-04-24

### Added
- Initial release of unified OpenGlaze
- Flask backend with REST API
- Vanilla JS frontend SPA
- SQLite/PostgreSQL dual database support
- Ory Kratos authentication integration
- Basic glaze CRUD operations
- Firing log tracking
- Photo documentation with gallery
- Recipe calculator with batch sizing
- Layering combination tracker
- User management and studio collaboration
- MIT license

[1.1.0]: https://github.com/KyaniteLabs/openglaze/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/KyaniteLabs/openglaze/releases/tag/v1.0.0
