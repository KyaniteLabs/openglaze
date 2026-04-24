# Skill Usage Example: Ceramic Glaze RE

This example shows how to use the `ceramic-glaze-re` skill to correctly identify a glaze from a photo.

---

## Example Scenario

You have a photo of a ceramic bowl and need to identify the glaze.

---

## Step 1: Read the Skill

```
Read .claude/skills/ceramic-glaze-re.md
```

This loads the systematic process, decision tree, and anti-patterns.

---

## Step 2: Collect Observations (MANDATORY)

Use the observation protocol from the skill:

| Attribute | Observation |
|-----------|-------------|
| **Primary base color** | Greenish-gray |
| **Undertones** | GREEN (sage, olive) |
| **Surface gloss** | High gloss |
| **Translucency** | Translucent |
| **Pooling behavior** | Darker where thick (in recesses) |
| **Color transitions** | Gradual |
| **Metallic effects** | Present in pooled areas |
| **Clay body** | Reddish-brown visible at rim |

---

## Step 3: Complete Family Comparison Matrix (MANDATORY)

**Do NOT skip this step. Score ALL families.**

| Family | Base Color | Surface | Pooling | Firing | Score |
|--------|------------|---------|---------|--------|-------|
| **Celadon** | ✓ Green-gray | ✓ Gloss, translucent | ✓ Darker where thick | ✓ Reduction | **4/4** |
| **Tenmoku** | ✗ Brown-black (not green) | ~ Semi-gloss | ~ | ✓ Reduction | 2/4 |
| **Shino** | ✗ White/orange | ✗ No crawling | ~ | ✓ Reduction | 1/4 |
| **Ash Glaze** | ~ Green-brown possible | ~ Variegated | ~ | ✓ | 2/4 |
| **Chun Blue** | ✗ Blue, not green | ~ | ~ | ✓ | 1/4 |

**Winner: CELADON (4/4)**

---

## Step 4: Use Decision Tree

```
START: What is PRIMARY base color?
→ GREEN or BLUE-GREEN
  → Translucent with glossy pooling?
    → CELADON ✓
```

---

## Step 5: Determine Firing Atmosphere

| Indicator | Observation | Indicates |
|-----------|-------------|-----------|
| Green undertones | Base color | Reduction (Fe²⁺) |
| Metallic in pools | Secondary | Reduction |
| Darker pooling | Characteristic | Reduction celadon |

**Conclusion: Reduction firing**

---

## Step 6: Identify Colorant

From the skill's colorant reference:

- Green in reduction = **Iron (Fe₂O₃)** at LOW concentration (0.5-2%)
- NOT high iron (6-10%) - that would produce brown/black

**Primary colorant: Iron oxide at 1.5%**

---

## Step 7: Reconstruct Recipe

From skill's family reference:

**Basic Celadon:**
| Material | % |
|----------|---|
| Potash Feldspar | 40% |
| Silica | 25% |
| Whiting | 15% |
| Kaolin | 15% |
| Ball Clay | 5% |
| Red Iron Oxide | 1.5% |

---

## Step 8: Assess Confidence

| Component | Confidence | Evidence |
|-----------|------------|----------|
| Glaze family (Celadon) | HIGH | 4/4 matrix score + decision tree match |
| Firing atmosphere | HIGH | Multiple reduction indicators |
| Iron as colorant | HIGH | Green in reduction = iron |
| Iron % (1.5%) | HIGH | Celadon requires low iron |
| Recipe base | MEDIUM | Standard celadon base |

**Overall: 85% confidence**

---

## Common Errors to Avoid

### ❌ WRONG Approach

1. See metallic sheen → "Must be Tenmoku!"
2. Skip comparison matrix
3. Use secondary features as primary signal
4. Result: **WRONG IDENTIFICATION**

### ✅ CORRECT Approach

1. Start with BASE COLOR (green = celadon branch)
2. Complete systematic comparison matrix
3. Score ALL families
4. Let data drive decision
5. Result: **CORRECT IDENTIFICATION**

---

## Quick Checklist

Before finalizing, verify:

- [ ] Read the skill file
- [ ] Collected all observations
- [ ] Completed family comparison matrix (ALL families scored)
- [ ] Used decision tree starting with BASE COLOR
- [ ] Checked Celadon vs Tenmoku distinction
- [ ] Did NOT anchor to secondary features (metallic, texture)
- [ ] Confirmed iron content matches family (low for celadon, high for tenmoku)
- [ ] Assessed confidence for each component
