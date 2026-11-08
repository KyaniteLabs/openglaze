# Foundation verification and remaining gaps

Baseline: `85367a28a1f3864d0d7b07c682cfb0e4bff6c07a` (master).

## Executed locally

Python 3.14.7, isolated environment, dependencies from requirements-dev.txt:

- `python -m pytest tests/ -q`: **175 passed** (includes two new inventory/read-contract tests).
- `black --check .`: **70 files unchanged**; Black emitted its Python-target
  auto-detection warning. No formatting failure.
- `ruff check .`: **passed**.
- `git diff --check`: **passed**.

Initial baseline suite: 172 passed, one failed because docs/index.html omitted
its explicit project-site/not-hosted-notebook clarification. Restored that
truthful text without weakening the chemistry/site contract test.

## Remediation in this change

Security-requested follow-up: pin Werkzeug to 3.1.9 instead of 3.1.8 to
remediate CVE-2026-102598 / SFTY-20261005-86121 (affected versions <3.1.9).
No Safety ignore or waiver was added. Exact-head hosted security checks remain
a required Security review/merge gate; this bump alone is not scan acceptance.

Added root architecture/product/read-before-work documents and a source-matched
owner inventory with regression checks. Forgejo workflow no longer masks pip,
lint or pytest failures, installs the actual requirements-dev.txt instead of
attempting editable installation of metadata-only pyproject.toml, and rejects
Python below 3.12. Runner image/version remains Platform's responsibility.

## Not verified / required follow-through

- Browser E2E exists, but no checked-in package manifest/Playwright runner
  configuration was found; browser execution was not performed. Engineering
  must provide a reproducible browser runner and wire it into CI.
- Container smoke is GitHub default-branch-push-only, not a PR gate; no local
  image build or container execution performed. Engineering/Platform must
  establish an exact-head pre-merge container check.
- GitHub Bandit step uses `|| true`; it is reporting, not an enforcing security
  gate. Security must judge and Engineering remediate baseline findings before
  changing that gate; no settings or .github workflow permission changes here.
- Hosted CI Python 3.12/3.13 and Forgejo execution are not local results; Security
  must check exact-head remote CI, secrets, exposure, blast radius and rollback.
- Mirror reconciliation remains **pending Platform**. README identifies a
  private maintainer mirror; that is not an authorized mapping or SHA receipt.
  No private mirror content/credentials were accessed or copied. Request an
  authorized identity/default-branch/SHA mapping and reconcile this PR after
  acceptance. Do not infer adoption from the GitHub branch.
- Open PR #175 proposes server decomposition; this map intentionally describes
  current master and must be reconciled if that PR lands first. PR #176 touches
  discovery text, not the new root documents.

Product reviews PRODUCT.md and user-facing descriptions first, then routes to
Security for exact-head review/merge. Builder does not merge. These remaining
gaps are routed on the root card, not exclusions: no partial-estate adoption.
Rollback is reverting this commit; no data migration, settings, secrets or
production deployment changes are included.
