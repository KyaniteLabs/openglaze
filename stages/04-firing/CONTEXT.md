# Stage 04 - Firing

**Purpose:** Fire the test and record conditions
**Input:** `03-application/output/app-log.md`
**Output:** `output/firing-log.md`

---

## Firing Variables

| Variable | Options |
|----------|---------|
| Kiln | [Which studio kiln] |
| Cone | 10 (target) |
| Atmosphere | Light, medium, heavy reduction |
| Body reduction | Yes/No, at what cone |
| Position | Top, middle, bottom shelf |
| Cooling | Normal, crash, slow cool |

---

## Firing Log Template

Write to `output/firing-log.md`:

```markdown
# Firing Log: [Date]

**Kiln:** [Name/ID]
**Date:** [YYYY-MM-DD]
**Firing #:** [Sequential number]

## Schedule

| Stage | Cone/Temp | Action | Notes |
|-------|-----------|--------|-------|
| Body reduction | Cone 010-08 | [gas setting] | [flame color, damper] |
| Glaze reduction | Cone 8-10 | [gas setting] | [flame color, damper] |
| Soak | [time at peak] | | |

## Atmosphere Log

- **Body reduction:** [Light/Medium/Heavy] - [Observations]
- **Glaze reduction:** [Light/Medium/Heavy] - [Observations]
- **Peak:** [Cone 10 bent how much?]

## Test Position

- Shelf: [Top/Middle/Bottom]
- Location: [Front/Back/Center/Side]

## Issues

- [Any problems during firing]

## Post-Fire Photo
[Link or note about photo location]
```

---

## Reference

Load `../ceramics-foundation/chemistry/firing-guide.md` for:
- Cone temperatures
- Reduction schedules
- Atmosphere monitoring

---

## Handoff

→ Proceed to `05-analysis/` to compare prediction to actual
