---
name: openglaze
description: Use OpenGlaze for ceramic glaze recipe analysis, UMF calculation, CTE estimation, batch scaling, material substitution research, and self-hosted pottery studio workflows. Trigger when an agent needs computational glaze chemistry help with real recipe strings.
---

# OpenGlaze

Use this skill when a task involves ceramic glaze recipes, UMF analysis, CTE risk, test-batch scaling, material substitutions, or OpenGlaze project work.

## Start Here

- Read `../../README.md` for setup, self-hosting, and safety framing.
- Use the CLI for direct local calculations: `python -m openglaze_cli`.
- Use the MCP server when an agent host should call glaze tools directly: `python -m openglaze_mcp`.
- Core chemistry lives under `../../core/chemistry/`.

## Workflow

1. Normalize the recipe string before analysis. Include material names and percentages.
2. Use `umf` or the `analyze_glaze_recipe` MCP tool before making chemistry claims.
3. Check `limit_warnings`, `missing_materials`, `thermal_expansion`, and `surface_confidence`.
4. Use batch scaling only after the recipe parses successfully.
5. Treat substitutions as test-tile candidates, not one-shot replacements.

## CLI Examples

```bash
python -m openglaze_cli brief
python -m openglaze_cli umf --recipe "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12" --cone 10
python -m openglaze_cli batch --recipe "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12" --size 500
python -m openglaze_cli substitutions --recipe "Custer Feldspar 50, Unobtainium 25, Silica 25"
```

## MCP Setup

```json
{
  "mcpServers": {
    "openglaze": {
      "command": "python",
      "args": ["-m", "openglaze_mcp"]
    }
  }
}
```

## Guardrails

- Do not present computed glaze fit as a substitute for fired test tiles.
- Do not make food-safety guarantees from UMF, CTE, or recipe data alone.
- When parsing fails or materials are missing, say so directly before offering alternatives.
- Keep advice practical for potters: next test, expected risk, and what to observe.
