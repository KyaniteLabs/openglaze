# Stage 05 - Analysis

**Purpose:** Compare prediction to actual result
**Input:** `04-firing/output/firing-log.md`, `02-prediction/output/prediction.md`
**Output:** `output/analysis.md`

---

## Analysis Checklist

1. **Color match?** - Compare predicted to actual
2. **Surface match?** - Gloss/matt/texture as expected?
3. **Surprises?** - What didn't you predict?
4. **Verdict** - Use again? Tweak? Avoid?

---

## Color Description

Use terms from `../ceramics-foundation/taxonomies/colors.md`:

- Not "green" → "celadon", "sage", "olive"
- Not "brown" → "tenmoku", "amber", "rust"
- Not "red" → "copper red", "iron red", "tomato"

---

## Surface Quality

Use terms from `../ceramics-foundation/taxonomies/glazes.md` section 4:

- Sheen: gloss, semi-gloss, satin, matt
- Texture: smooth, micro-crystal, macro-crystal
- Variation: even, breaking at edges, pooled
- Movement: static, flowing, running

---

## Analysis Template

Write to `output/analysis.md`:

```markdown
# Analysis: [Glaze A] over [Glaze B]

## Prediction vs Actual

| Factor | Predicted | Actual | Match? |
|--------|-----------|--------|--------|
| Color | [from prediction] | [observed] | ✓/✗ |
| Surface | [from prediction] | [observed] | ✓/✗ |
| Running | [from prediction] | [observed] | ✓/✗ |

## Color Description
[Using colors.md terms]

## Surface Description
[Using surface quality terms]

## Surprises
[What you didn't expect]

## Why Prediction Was Right/Wrong
[Learning for next time]

## Verdict
- [ ] **Production ready** - Use as-is
- [ ] **Interesting** - Try variations
- [ ] **Failed** - Do not repeat
- [ ] **Inconclusive** - Retest with controls

## Photo
[Link to fired result photo]
```

---

## Handoff

→ Proceed to `06-documentation/` to create reproducible recipe
