# Public notebook implementation plan

**Goal:** Give the public OpenGlaze site a distinctive, accessible specimen-notebook presentation with honest computational evidence.

**Architecture:** Keep static HTML/CSS and native navigation; no new runtime dependency, service or application behavior. Preserve canonical metadata and existing public destinations. Split reviewable changes into accessibility foundations and notebook content/presentation as needed.

**Tech Stack:** Existing HTML/CSS, Python/pytest contracts, installed Playwright/Chrome for rendered verification.

1. Run the clean baseline suite. Write rendered regression assertions for mobile navigation, action/text contrast and reduced motion; confirm the current page fails for the observed reasons.
2. Modify `docs/index.html` foundations: readable colors, visible navigation at narrow widths, visible focus, native anchor focus and reduced-motion handling. Re-run the browser assertions and keyboard traversal.
3. Replace the generic hero/mockups with the verified recipe/UMF example and explicit calculation caveats. Replace the stale homepage test-count assertion in `tests/test_seo_contracts.py` with a calculation-versus-engine contract; observe it fail before implementation. Preserve guide destinations and maintain product claims.
4. Refine existing layout/CSS into ruled notebook composition, fewer repeated cards and distinct workflow sections. Capture desktop/mobile screenshots; test all requested widths and OS preferences. Run the actual installed `gate-audit.js`; document limits instead of claiming certification.
5. Update `CHANGELOG.md`, run full pytest, existing CI formatter and lint, and check the diff. Keep PRs scoped and reviewable; use a series if needed to stay within the repository's meaningful-change limit.
6. Recheck authenticated included Blacksmith coverage before CI, create normal PRs without review bots, inspect checks, merge after success, verify Pages deployment and public bytes against the merged SHA. Preserve prior branches and keep issues open. Record evidence outside the repository.
