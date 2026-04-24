# Glaze Chemistry

## Molecular Formulas for Common Materials

### Basic Materials

| Material | Formula | Role | Molecular Weight | Notes |
|----------|---------|------|------------------|-------|
| Silica | SiO₂ | Glass former - creates main glass structure | 60.1 | Quartz, flint |
| Alumina | Al₂O₃ | Stabilizer - thickens melt, prevents running | 101.8 | Kaolin, alumina hydrate |
| Whiting (Calcium Carbonate) | CaCO₃ | High-temp flux, hardens glaze | 100.1 | 43.9% LOI, yields 56.1% CaO |
| Dolomite | CaMg(CO₃)₂ | Flux - provides both CaO and MgO | 184.4 | 47.61% LOI, yields 30.48% CaO, 21.91% MgO |
| Talc | Mg₃Si₄O₁₀(OH)₂ | Flux and opacifier | 379.3 | Contributes MgO and SiO₂ |

### Feldspars

| Material | Theoretical Formula | Typical Analysis |
|----------|---------------------|------------------|
| **Potash Feldspar** | K₂O·Al₂O₃·6SiO₂ | SiO₂: 64-69%, Al₂O₃: 17-18.5%, K₂O: 10-17% |
| Varieties: | Custer, G-200, K200, Primas P | Most common feldspar in glazes |
| **Soda Feldspar** | Na₂O·Al₂O₃·6SiO₂ | SiO₂: 68-72%, Al₂O₃: 19-20%, Na₂O: 8-12% |
| Varieties: | Kona F-4, Nepheline Syenite 270x/400x, Calspar | |
| **Nepheline Syenite** | (Na,K)AlSiO₄ | SiO₂: 58-62%, Al₂O₃: 22-24%, Na₂O: 10-12%, K₂O: 4-6% |
| Note: | Lower silica, higher alumina than feldspars | NOT direct substitute for potash |

### Common Colorants

| Colorant | Formula | Oxide Content | Notes |
|----------|---------|---------------|-------|
| Copper Carbonate | CuCO₃ | ~64-65% CuO | Greens, blues, reds (atmosphere dependent) |
| Copper Oxide | CuO | ~100% CuO | 1.55× stronger than carbonate |
| Iron Oxide Red | Fe₂O₃ | ~95% Fe₂O₃ | Most common iron oxide |
| Cobalt Carbonate | CoCO₃ | ~63% CoO | Powerful blue |
| Cobalt Oxide | Co₃O₄ | ~93% CoO | 1.48× stronger than carbonate |
| Manganese Dioxide | MnO₂ | ~100% MnO (effective) | Purples, browns |
| Manganese Carbonate | MnCO₃ | ~61-62% MnO | 1.62× weaker than dioxide |
| Rutile | TiO₂·Fe₂O₃ | Varies | Tans, browns, blues (Ti + Fe) |

---

## Unity Molecular Formula (UMF)

### Definition
Also called **Seger Formula** - an oxide formula normalized so that flux oxides (RO/R₂O) total **1.0**.

### Purpose
- Standardize glaze formulas for comparison across different recipes
- Reveal true oxide balance that determines melting behavior
- Essential for glaze stability and predicting defects (crazing, shivering)
- Required for material substitutions without changing glaze behavior

### Calculation Method
1. Convert recipe percentages to oxide moles using molecular weights
2. Sum all flux oxides (K₂O, Na₂O, CaO, MgO, etc.)
3. Divide all oxide amounts by the total flux sum
4. Result: fluxes = 1.0, other oxides shown relative to flux

### Worked Example

**Raw Formula (oxide moles):**
```
K₂O:  0.6
CaO:  1.3
MgO:  0.2
ZnO:  0.1
Al₂O₃: 0.9
SiO₂: 9.0
```

**Step 1: Sum fluxes**
0.6 + 1.3 + 0.2 + 0.1 = **2.2**

**Step 2: Divide all by 2.2**
```
K₂O:  0.6 ÷ 2.2 = 0.27
CaO:  1.3 ÷ 2.2 = 0.59
MgO:  0.2 ÷ 2.2 = 0.09
ZnO:  0.1 ÷ 2.2 = 0.05
Al₂O₃: 0.9 ÷ 2.2 = 0.41
SiO₂: 9.0 ÷ 2.2 = 4.09
```

**Unity Formula:**
```
Fluxes: 0.27 K₂O, 0.59 CaO, 0.09 MgO, 0.05 ZnO (sum = 1.0)
Al₂O₃: 0.41
SiO₂:  4.09
```

---

## Flux:Alumina:Silica Target Ranges

### Key Ratios

#### Silica:Alumina Ratio
- **Formula:** SiO₂ ÷ Al₂O₃ (in UMF)
- **Glossy surfaces:** > 5:1 (Stull chart; Glazy.org)
- **Semi-matte (satin):** ~4:1 to 5:1
- **Matte surfaces:** < 4:1
- **Note:** Original Stull chart context is cone 11 with 0.3 R₂O : 0.7 RO (calcium). Ratios shift at other cones.

#### Flux Ratio
- **Definition:** Ratio of alkali (R₂O) to alkaline earth (RO) fluxes
- **High alkali (0.3+):** Higher expansion, more fluid, prone to crazing
- **Balanced (0.2-0.3):** Common for stable glazes
- **High alkaline earth (0.8+):** Lower expansion, stiffer melt, promotes mattes

### Target Ranges by Temperature

| Temperature Range | Alumina (Al₂O₃) | Silica (SiO₂) | Notes |
|-------------------|-----------------|---------------|-------|
| **Cone 06-04 (Low Fire)** | 0.1 - 0.3 | 1.5 - 3.0 | Requires strong boron fluxing |
| **Cone 1-6 (Mid Range)** | | | |
| — Glossy | 0.25 - 0.4 | 2.5 - 4.0 | Higher boron often present |
| — Satin | 0.2 - 0.4 | 2.0 - 3.5 | |
| — Matte | 0.2 - 0.5 | 2.0 - 3.0 | |
| **Cone 8-10 (High Fire)** | | | |
| — Glossy | 0.3 - 0.6 | 3.0 - 6.0 | Wider silica ranges possible |
| — Satin | 0.35 - 0.6 | 2.0 - 5.0 | |
| — Matte | 0.35 - 0.8 | 2.0 - 5.0 | |

### Stability Importance
- **Glaze Durability:** Proper Al₂O₃ and SiO₂ levels ensure chemical resistance
- **Thermal Expansion:** Flux ratios and silica levels determine CTE
- **Melt Behavior:** Al₂O₃ prevents excessive running; SiO₂ ensures glass formation
- **Surface Defects:** Outside limits risks crazing, shivering, pinholing, or leaching

---

## Material Substitution Chart

### Substitution Principles
1. **Oxide Matching:** Maintain oxide balance, not just recipe weight
2. **Test Essential:** Always mix small test batches first
3. **Particle Size:** Match mesh size when possible
4. **Chemical Analysis:** Use supplier data sheets

### One-to-One Substitutions

| Substituting From | To | Ratio | Notes |
|-------------------|---------|--------|-------|
| **Cobalt Oxide** | Cobalt Carbonate | 1 : 1.48 | Oxide is 93% CoO; carbonate is 63% CoO |
| Cobalt Carbonate | Cobalt Oxide | 1 : 0.68 | |
| **Copper Oxide** | Copper Carbonate | 1 : 1.55 | Oxide is 100% CuO; carbonate is 64-65% CuO |
| Copper Carbonate | Copper Oxide | 1 : 0.64 | |
| **Manganese Dioxide** | Manganese Carbonate | 1 : 1.62 | MnO₂ is 100% MnO; carbonate is 61-62% MnO |
| Manganese Carbonate | Manganese Dioxide | 1 : 0.62 | |
| **Whiting** | Wollastonite | 1 : 1.16 | Whiting is 56% CaO; Wollastonite is 48% CaO + 52% SiO₂ |
| Wollastonite | Whiting | 1 : 0.86 | Reduce silica by ~6% when substituting wollastonite |
| **Barium Carbonate** | Strontium Carbonate | 1 : 0.75 | BaCO₃ is 77.5% BaO; SrCO₃ is 70% SrO |
| Strontium Carbonate | Barium Carbonate | 1 : 1.33 | Strontium is LESS toxic than barium |
| **Red Iron Oxide** | Yellow Iron Oxide | 1 : 1.08 | Yellow is 88% Fe₂O₃; Red is 95% Fe₂O₃ |
| Yellow Iron Oxide | Red Iron Oxide | 1 : 0.93 | |

### Complex Substitutions

#### Dolomite Replacement
- **Original:** Dolomite (CaMg(CO₃)₂)
- **Substitute:** Equal parts whiting + magnesium carbonate
- **Example:** 10% dolomite → 5% whiting + 5% magnesium carbonate
- **Note:** Close match but not exact due to trace elements

#### Feldspar Substitutions
- **Principle:** Choose from same group (potash, soda, or lithium)
- **Potash Group:** Custer, G-200, K200, Primas P
- **Soda Group:** Kona F-4, Nepheline Syenite, Calspar, NC-4
- **Important:** Nepheline syenite is NOT a direct substitute for potash feldspar

#### Gerstley Borate Replacement
- **Original:** Gerstley Borate (calcium borate ore)
- **Substitutes:**
  - Colemanite (calcium borate)
  - Boron frits (e.g., Ferro 3134)
  - Borax (soluble - use calcined borax)
- **Note:** Both Gerstley Borate and Colemanite are variable

#### Albany Slip Replacements
- **Original:** Albany Slip (no longer mined)
- **Substitutes:**
  - Alberta Slip
  - Seattle Slip
  - Sheffield Slip Clay Formula
  - A.R.T. Albany Slip Synthetic
- **Note:** Matching depends on amount in recipe, temperature, and atmosphere

### Nigel's Percentage Method
**Purpose:** Recreate glazes from oxide analysis using available materials

**Steps:**
1. List target oxide percentages (SiO₂, Al₂O₃, CaO, KNaO, etc.)
2. Choose raw materials to supply each oxide
3. Start with most complex material (e.g., feldspar for KNaO)
4. Calculate parts needed: (Target %) ÷ (Oxide % in material) × 100
5. Subtract supplied oxides from target
6. Repeat for next oxide until all are supplied
7. Sum parts and optionally normalize to 100%

**Automation:** Glazy's Target & Solve feature can automate this process

---

## Authoritative Sources

| Source | Focus | Key Resources |
|--------|-------|---------------|
| **Digitalfire** | Technical glaze chemistry, limit formulas | Glaze Chemistry Basics, Limit Formulas, Unity Formula glossary |
| **Ceramic Materials Workshop** | UMF education, Extended UMF | UMF Calculator spreadsheet, Extended UMF approach |
| **Glazy** | Online glaze database, calculation tools | Chemical Analyses, Material Substitution, Limit Formulas, Target & Solve |
| **Ceramic Arts Network** | Practical recipes, substitutions | Glaze Material Substitutions article, Feldspars article |
| **Mastering Glazes** | Comprehensive formulation | John Britt / John Hesselberth & Ron Roy |

---

*Source: ../../research-pipeline-prod/ceramics-foundation/research/r1-glaze-chemistry.json*
