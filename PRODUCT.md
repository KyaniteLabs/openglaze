# OpenGlaze

A ceramic studio workbench for organizing glazes and layered combinations, tracking experiments/photos from idea to fired/documented result, and exploring recipe chemistry before making a test tile. It combines a browser studio, deterministic chemistry tools and optional Kama AI assistance—not a kiln controller or safety certification service.

## What exists

- A Flask/vanilla-JavaScript studio with combinations, glaze library, photos, experiment progress, predictions, basics and Kama panel. Personal mode uses local SQLite; cloud mode adds auth/multi-user boundaries and requires its own operational verification.
- A shared chemistry library plus CLI and dependency-free stdio MCP adapter for UMF, predicted surface/CTE, compatibility, color, substitution and search. These are heuristics/calculations, not observed firing outcomes.
- Kama retrieval/prompt/streaming and provider adapters. AI is optional; model/endpoints determine whether prompts/recipe context leave the host. Personal config advertises Ollama with `kimi-k2.5:cloud`; do not equate “personal” or a localhost API with offline/private inference.
- Bundled `ceramics-foundation` reference data: 36 materials, 21 oxides, 7 colorants, 8 clay bodies, 8 demo glazes, 15 chemistry rules, 106 seed chemistry rules; plus firing/schedules, UMF target ranges, thermal-expansion, substitutions, layering, surface-prediction and food-safety guidance. These are source counts, not independently validated scientific coverage. Studio schemas/templates are not all valid JSON (the studio-profile schema is a placeholder).

## Evidence and limits

A local personal studio with a fresh synthetic/seeded database rendered real combination cards in Chromium; 54 chemistry tests passed. CLI UMF worked for a synthetic Custer Feldspar/silica/whiting/EPK recipe. No AI request, cloud account, real studio data, upload, kiln action or payment was exercised.

Food-safety labels, CTE compatibility and AI advice cannot establish leach resistance, firing safety or fitness for functional ware: test materials/results independently. The seeded library and screenshots are not user firing evidence. Browser assets include a CDN dependency, so a fully offline experience also needs checking. See [ARCHITECTURE.md](ARCHITECTURE.md) and [docs/architecture.md](docs/architecture.md).
