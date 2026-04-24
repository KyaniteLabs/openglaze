# Stage 06 - Documentation

**Purpose:** Create reproducible combo recipe
**Input:** `05-analysis/output/analysis.md`
**Output:** `output/combo-recipe.yaml`

---

## Documentation Template

Write to `output/combo-recipe.yaml`:

```yaml
name: "[Glaze A] over [Glaze B]"
created: [YYYY-MM-DD]
verdict: [production/interesting/failed]

combo:
  base: "[Glaze B - dipped first]"
  top: "[Glaze A - dipped second]"

application:
  method: [dip/pour/spray]
  base_time: [seconds]
  top_time: [seconds]
  dry_between: [time]

result:
  color: "[from analysis - use colors.md terms]"
  surface: "[gloss/matt/etc]"
  breaking: "[how it looks at thin areas]"
  movement: "[static/flowing/running]"

firing:
  cone: 10
  atmosphere: "[light/medium/heavy reduction]"

notes: |
  [Key observations, what worked, what didn't]

photo: "[link to image]"

related_combos:
  - "[similar successful combos]"
```

---

## Archive Filing

Based on verdict:

| Verdict | Destination | Action |
|---------|-------------|--------|
| Production | `archive/successful/` | Use on sale pieces |
| Interesting | `archive/successful/` with notes | Schedule variation |
| Failed | `archive/failed/` | Document what went wrong |
| Inconclusive | `archive/pending/` | Add to retest queue |

---

## Copy to Archive

```bash
cp output/combo-recipe.yaml ../archive/[successful|failed|pending]/
```

---

## Update Progress

Add to `PROGRESS.md`:

- If successful: Add to "Known Successful Combos"
- If failed: Note briefly what went wrong
- If pending: Add to retest queue

---

## Pipeline Complete

Experiment finished. Start new experiment with `experiment [A] over [B]`.
