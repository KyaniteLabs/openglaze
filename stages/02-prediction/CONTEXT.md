# Stage 02 - Prediction

**Purpose:** Forecast what the combo will look like
**Input:** `01-ideation/output/combo.md`
**Output:** `output/prediction.md`

---

## Prediction Factors

| Factor | How to Assess | From Foundation |
|--------|---------------|-----------------|
| Opacity interaction | Will top show through? | `taxonomies/glazes.md` opacity notes |
| Color mixing | Will colors blend or stay distinct? | `chemistry/glaze-chemistry.md` colorant behavior |
| Surface texture | Gloss over matt = ? | `taxonomies/glazes.md` surface quality |
| Fluidity | Will either run? | `glaze-lab/prediction-framework.md` stability |

---

## Prediction Template

Write to `output/prediction.md`:

```markdown
# Prediction: [Glaze A] over [Glaze B]

## Expected Color
[Description using terms from colors.md]

## Expected Surface
- Sheen: [gloss/semi-gloss/matt]
- Texture: [smooth/variable/crystalline]
- Breaking: [where it thins]

## Concerns
- [ ] Running risk
- [ ] Crawling risk
- [ ] Muddy result risk

## Confidence
- [ ] Wild guess
- [ ] Educated guess (similar combos exist)
- [ ] High confidence (chemistry predicts clearly)

## Comparison Point
[Similar to known combo X / Unlike anything tested]
```

---

## Chemistry-Based Predictions

Load `../ceramics-foundation/chemistry/glaze-chemistry.md` for:

- Copper + reduction = red (but copper over clear = green-red blend?)
- Iron glazes blend toward brown/black
- Shinos trap carbon = orange/gray variation
- High boron = more fluid = more blending

---

## Handoff

→ Proceed to `03-application/` to apply and log
