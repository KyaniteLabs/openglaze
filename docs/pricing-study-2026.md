# OpenGlaze Pricing Study — Reality-Based, April 2026

> **Status:** Research complete. Replaces fabricated pricing tiers removed in commit `3385f4a`.  
> **Product:** OpenGlaze is a computational glaze chemistry tool. It calculates Unity Molecular Formula (UMF), Coefficient of Thermal Expansion (CTE), and computationally optimizes ceramic glaze recipes to reduce physical test tiles. It is NOT a recipe database, social platform, or community. It is a scientific/engineering tool for potters who mix their own glazes.

---

## 1. Executive Summary

**What OpenGlaze does:** Takes a glaze recipe (e.g., "Feldspar 40%, Silica 30%, Whiting 15%, Kaolin 10%, Zinc Oxide 5%") and tells you:
- The UMF — molecular ratios of fluxes, alumina, and silica
- Whether the CTE matches your clay body (prevents crazing/shivering)
- How to adjust the recipe to hit a target property (lower CTE, more matte, less runny, etc.)

**The value proposition is purely economic:** Every test tile that doesn't need to be fired saves materials, kiln energy, and potter time. For a production potter or studio, this is directly quantifiable.

**Recommended model:** **Open Core + Value-Based Subscription**. Core UMF/CTE calculator remains free and MIT-licensed forever. The recipe optimizer and batch analysis are premium features.

**Recommended price points:**

| Tier | Price | Who | What They Get |
|------|-------|-----|---------------|
| **Calculator** | **$0** | All potters | UMF calc, CTE check, recipe storage, self-host |
| **Optimizer** | **$8/mo or $80/yr** | Serious potters, production potters | Recipe optimizer, batch costing, material substitutions, export |
| **Studio** | **$29/mo or $290/yr** | Teaching studios, small manufacturers | Team sharing, batch history, firing logs, API |
| **Lab** | **Custom** | Universities, manufacturers, research | Custom material DB, SLA, training, priority support |

---

## 2. What OpenGlaze Actually Is (And Isn't)

### Is
- A **computational chemistry engine** for ceramic glazes
- A tool that reduces physical test tiles through mathematical prediction
- MIT-licensed open source software
- Self-hostable by anyone with technical skill

### Is Not
- A recipe database (that's Glazy)
- A social network or community
- A studio management tool (that's Kiln Fire)
- A marketplace for materials or supplies

**Key implication:** OpenGlaze is a **specialized scientific tool**, not a social platform. Pricing should align with other niche technical/creative tools, not with social SaaS.

---

## 3. The Real Economics

### 3.1 What Test Tiles Actually Cost

A potter developing a new glaze typically fires 5–20 test tiles per recipe iteration.

| Cost Component | Per Tile | 10-Tile Cycle |
|----------------|----------|---------------|
| Clay body (bisque tile) | $0.20–$0.50 | $2–$5 |
| Glaze materials | $0.30–$1.00 | $3–$10 |
| Kiln firing (electric, per piece) | $0.50–$1.50 | $5–$15 |
| Potter's time (15 min/tile @ $20/hr) | $5.00 | $50 |
| **Total** | **~$6–$8** | **~$60–$80** |

**If the optimizer reduces test cycles from 3 to 2:** That's **$60–$80 saved per glaze development**. For a potter developing 6 glazes per year: **$360–$480 saved annually**.

### 3.2 What Production Potters Spend

| Expense | Annual Cost |
|---------|-------------|
| Clay and materials | $500–$5,000 |
| Kiln firings (electric/gas) | $300–$2,000 |
| Studio rent/membership | $1,200–$3,600 |
| Glaze materials (commercial) | $200–$1,000 |
| **Or: mixing own glazes** | **$100–$500** |

A production potter mixing their own glazes to save money is exactly the user who benefits from optimization. They already do the math manually or not at all.

### 3.3 Value-Based Price Anchor

SaaS best practice: charge 10–20% of the value created.

- Value created: $360–$480/year in saved materials/time
- 10–20% of value: **$36–$96/year**
- **Recommended annual price: $80/year** — within the value range, feels like a tool purchase
- Monthly equivalent: **$8/month** — low enough to not think twice

---

## 4. Competitive Landscape (Corrected)

### Direct Competitors (Glaze Calculation Tools)

| Product | Price | Model | What It Does |
|---------|-------|-------|--------------|
| **PotterPal** | ~$30–$50 one-time | Desktop software (Win/Mac) | UMF charts, material analysis, recipe comparison. Older, static. |
| **Glazy** | Free | Community-funded | UMF calc, recipe DB, kiln schedules. No optimization engine. |
| **Spreadsheets** | $0 (Excel/Google Sheets) | Self-built | Many potters build their own UMF calculators. Fragile, time-intensive. |
| **OpenGlaze** | $0 / $8/mo / $29/mo | Open core + SaaS | UMF, CTE, computational optimizer. Self-hostable or hosted. |

**Key insight:** There is NO direct competitor to the optimizer. Glazy calculates but doesn't optimize. PotterPal is static charts, not algorithmic suggestions. Spreadsheets are DIY. OpenGlaze's recipe optimizer is genuinely unique in this space.

### Adjacent Tools (Different Problem)

| Product | Price | What It Does |
|---------|-------|--------------|
| **Kiln Fire** | $29/mo | Studio management: firing fees, memberships, classes |
| **GatherGrove** | $29–$200/mo | Pottery club management |
| **Ceramispace** | Unknown | Recipe tracking, firing schedules (iOS/Mac) |

These are not competitors. A studio might use Kiln Fire ($29) AND OpenGlaze Optimizer ($8) — they solve different problems.

---

## 5. Recommended Pricing Architecture

### Philosophy

> **"The calculator is a gift. The optimizer is a product."**

The UMF/CTE calculator is the entry point — it proves the science works. The optimizer is where the economic value lives. A potter can verify their recipes for free; paying unlocks the tool that *reduces* how many recipes they need to verify physically.

### Tier Details

#### Calculator — $0 (Free Forever, MIT Licensed)

**Target:** All potters, students, hobbyists

**Includes:**
- Full UMF calculation and Stull chart visualization
- CTE mismatch detection against clay bodies
- Unlimited recipe storage (local or self-hosted)
- Standard oxide material database
- Community support

**Rationale:** This tier must be genuinely useful standalone. It demonstrates accuracy and builds trust. The marginal cost of a self-hosted user is zero.

#### Optimizer — $8/month or $80/year (Save $16)

**Target:** Production potters, serious hobbyists, glaze developers

**Unlocks:**
- **Recipe Optimizer** — algorithmic suggestions to hit target CTE, surface, alkali, running risk
- **Material Substitutions** — suggest cheaper or available alternatives
- **Batch Cost Calculator** — input material prices, see per-batch and per-piece costs
- **Export** — PDF recipe cards, CSV, print-friendly
- **Cloud Sync** — recipes across devices
- **Custom Materials** — add non-standard oxides, local materials

**Rationale:** $8/month is below virtually every SaaS tool a potter might use. At $80/year, it pays for itself if it eliminates just one test tile cycle. The annual discount (17%) encourages commitment.

#### Studio — $29/month or $290/year (Save $58)

**Target:** Teaching studios, community ceramics centers, small production shops

**Unlocks (everything in Optimizer, plus):**
- **Team Sharing** — shared recipe libraries with read/write permissions
- **Batch History** — track every batch mixed, who mixed it, when
- **Firing Log Integration** — link recipes to kiln firings, record results
- **API Access** — integrate with studio management tools
- **Priority Support** — email support, video call option
- **White-label Export** — recipes branded with studio logo

**Rationale:** $29/month matches Kiln Fire's pricing — studios already budget at this level. The annual plan at $290 (17% discount) is designed for institutions that plan yearly.

#### Lab — Custom

**Target:** University ceramics departments, manufacturers, research labs

**Includes:**
- Everything in Studio
- SSO / SAML authentication
- Custom material database (institution-specific raw materials with lab-tested properties)
- Audit logs and compliance reporting
- Dedicated support channel with SLA
- Training sessions for faculty/staff
- Volume pricing

**Rationale:** Universities have software budgets. A ceramics department with 50+ students using the tool is worth a $500–$2,000/year license. Custom pricing allows procurement-friendly invoicing.

### Self-Host vs. SaaS

| | Self-Host (Free) | SaaS (Paid) |
|---|---|---|
| Code | Full source, MIT license | Same source, hosted |
| Features | Calculator only (no optimizer) | Tier-dependent |
| Data | Local storage | Cloud sync, backups |
| Support | Community | Priority |
| Updates | Manual pull | Automatic |

The self-hosted version gets the Calculator free forever. The Optimizer module is closed-source and only available via SaaS or a separate license key. This is the Open Core model.

---

## 6. Why This Isn't Traditional SaaS Pricing

| Traditional SaaS Assumption | OpenGlaze Reality |
|-----------------------------|-------------------|
| "Charge per seat" | Most users are solo potters. Team sharing is a Studio feature, not the default. |
| "Freemium conversion 2–5%" | The free tier is a scientific calculator. The paid tier is an optimizer. Different jobs. Conversion will be higher because the value gap is clearer. |
| "Enterprise at $299/mo" | There are no ceramic glaze enterprises. The top is universities and small manufacturers. |
| "Usage-based pricing" | Potters don't think in API calls. Flat monthly is simpler. |
| "$29 is the floor for B2B" | Potters are individuals, not businesses. $8 is accessible to hobbyists. |

---

## 7. Revenue Projections (Conservative)

### Assumptions

- Year 1: 1,500 active users (niche tool, realistic)
- Calculator-to-Optimizer conversion: 8% (higher than typical freemium because the value proposition is purely economic)
- Optimizer-to-Studio conversion: 15% of paid users
- Annual plan adoption: 35%
- Churn: 4% monthly

### Year 1

| Metric | Value |
|--------|-------|
| Active users | 1,500 |
| Optimizer subscribers | 120 |
| Studio subscribers | 18 |
| MRR | ~$1,482 |
| Annual revenue | ~$17,800 |

### Year 3 (Growth)

| Metric | Value |
|--------|-------|
| Active users | 5,000 |
| Optimizer subscribers | 400 |
| Studio subscribers | 60 |
| MRR | ~$4,940 |
| Annual revenue | ~$59,300 |
| Lab deals | 3–5 at $500–$1,500/yr |
| **Total Annual** | **~$62,000–$67,000** |

### Reality Check

$60K–$70K/year by Year 3 is modest. It covers:
- Server costs: $100–$500/month
- Part-time development: sustainable
- Open source maintenance: no burnout

This is a **lifestyle business** that serves a community, not a startup.

---

## 8. Implementation Roadmap

### Phase 1: Open Core Split (Month 1–2)

Separate the codebase:
```
openglaze-core/     → MIT (UMF, CTE, recipe storage)
openglaze-optimizer/ → Proprietary (optimization algorithm)
```

- Core remains fully open, self-hostable
- Optimizer is a closed-source module loaded by the SaaS
- Feature flags determine access level

### Phase 2: Billing Infrastructure (Month 2–3)

- Stripe integration for subscriptions
- GitHub Sponsors as alternative ($8/mo tier mapped to Optimizer)
- Annual billing with 17% discount
- Student/teacher verification (.edu email = Optimizer free)

### Phase 3: SaaS Launch (Month 3–4)

- Hosted calculator free (no signup required)
- Signup required for Optimizer (14-day trial)
- Cloud sync, export tools, custom materials

### Phase 4: Studio & Lab Tiers (Month 6–12)

- Team sharing, batch management
- API documentation
- Direct outreach to university ceramics departments

---

## 9. What the Removed Tiers Got Wrong

| Removed Tier | Problem | Fix |
|--------------|---------|-----|
| Free $0 | Actually correct for Calculator | Keep, but clarify what's included |
| Pro $9/mo | Price was okay but features were vague | Renamed to Optimizer, features specified |
| Studio $29/mo | Same price but no differentiation from Kiln Fire | Added team sharing, batch history, API — features a studio actually needs |
| Education $199/yr | Annual-only, no monthly option | Added .edu verification for free Optimizer; Lab tier for institutions |

The original tiers were fabricated with no connection to actual features, costs, or user needs.

---

## 10. Summary

| Question | Answer |
|----------|--------|
| **Who is the customer?** | Potters who mix their own glazes and fire test tiles. |
| **What do they pay for?** | Reducing test tiles. $8/mo saves $60+ per glaze cycle. |
| **What's free?** | UMF calculator, CTE check, recipe storage, self-hosting. |
| **What's paid?** | Optimizer, batch costing, cloud sync, team features. |
| **What's the ceiling?** | $60–$70K/year by Year 3. Lifestyle business scale. |
| **How is this different from Glazy?** | Glazy calculates and stores. OpenGlaze optimizes. Different jobs. |

---

*Document version: 2.0 — April 2026*  
*Next review: After SaaS launch or 1,000 active users*
