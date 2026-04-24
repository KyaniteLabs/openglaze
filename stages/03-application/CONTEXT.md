# Stage 03 - Application

**Purpose:** Apply glazes and log the process
**Input:** `02-prediction/output/prediction.md`
**Output:** `output/app-log.md`

---

## Application Variables

| Variable | Options |
|----------|---------|
| Method | Dip, pour, spray |
| Base dip time | 3 sec, 5 sec, 10 sec |
| Dry time between layers | None, 5 min, fully dry |
| Top dip time | 3 sec, 5 sec, 10 sec |
| Test piece | Tile, small pot, reject piece |

---

## Application Log Template

Write to `output/app-log.md`:

```markdown
# Application Log: [Glaze A] over [Glaze B]

**Date:** [YYYY-MM-DD]
**Test Piece:** [Description or ID]

## Application Sequence

### Base Layer ([Glaze B])
- Method: [dip/pour/spray]
- Time: [seconds or passes]
- Observations: [thickness, evenness]

### Dry Time
- Between layers: [time]

### Top Layer ([Glaze A])
- Method: [dip/pour/spray]
- Time: [seconds or passes]
- Observations: [thickness, evenness]

## Label
[Code written on piece - e.g., "TC-CW" = Tom Coleman over Choinard White]

## Pre-fire Photo
[Link or note about photo location]
```

---

## Tips

- Consistent dip times = reproducible results
- Label BEFORE glazing (pencil on bisque)
- Photo unfired piece (shows application thickness)
- Use same clay body as production pieces

---

## Handoff

→ Proceed to `04-firing/` to fire and log atmosphere
