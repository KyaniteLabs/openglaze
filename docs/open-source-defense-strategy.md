# OpenGlaze Defense Strategy: Protecting a Niche Scientific Tool

> **Product context:** OpenGlaze is a computational glaze chemistry engine — UMF calculator, CTE analyzer, and recipe optimizer. It is MIT-licensed open source. It is NOT a social platform, recipe database, or community. The threat model for a niche scientific tool is fundamentally different from infrastructure SaaS.

---

## 1. Threat Assessment: What's Actually at Risk?

### The Realistic Threats

| Threat | Likelihood | Impact | Notes |
|--------|-----------|--------|-------|
| A developer forks the calculator and hosts it | Medium | Low | Calculator is MIT — forks are expected and fine. No optimizer = no economic value. |
| Someone copies the optimizer algorithm | Low | High | The optimizer is the proprietary moat. This is the actual asset to protect. |
| A pottery supply company adds glaze calc to their site | Low | Medium | They have distribution but lack the algorithmic depth. |
| AWS/Google/Azure hosts "Managed OpenGlaze" | **Near zero** | N/A | The ceramics market is too small for cloud vendors to care. |

### What You're Actually Protecting

OpenGlaze has two distinct assets with different risk profiles:

1. **The Calculator (UMF, CTE)** — MIT-licensed, open, forkable. This is a commodity. The UMF formula is public knowledge. The code implementation is useful but not unique.

2. **The Optimizer Algorithm** — Proprietary. This is the search heuristic, the scoring function, the material substitution logic, the guards and edge-case handling. This is what took engineering effort and what competitors would actually want.

**Verdict:** The defense strategy is not about preventing forks of the calculator. It's about protecting the optimizer algorithm while still being genuinely open source.

---

## 2. The Right Model: Open Core

### Architecture

```
┌─────────────────────────────────────────┐
│           openglaze-core                │
│  (MIT License — forever open)           │
│  - UMF calculator                       │
│  - CTE analyzer                         │
│  - Recipe parser and storage            │
│  - Standard material database           │
│  - Stull chart visualization            │
│  - REST API (calculation endpoints)     │
└─────────────────────────────────────────┘
                   │
                   ▼ (loads at runtime)
┌─────────────────────────────────────────┐
│        openglaze-optimizer              │
│  (Proprietary — licensed module)        │
│  - Recipe optimization algorithm        │
│  - Material substitution engine         │
│  - Scoring and ranking heuristics       │
│  - Batch cost calculator                │
│  - Export generators                    │
└─────────────────────────────────────────┘
```

### How It Works

- `openglaze-core` is a complete, useful tool on its own. Self-host it, fork it, sell it — MIT license allows all of it.
- `openglaze-optimizer` is a binary module (compiled Python extension, or separate service) that `core` loads if a valid license key is present.
- The SaaS hosted version includes both. Self-hosted free version includes only core.
- Users who want the optimizer either: (a) pay for SaaS, or (b) purchase a license key for self-hosted use.

### Why This Is Fair

- The calculator uses public-domain ceramic chemistry formulas. Charging for it would be unethical.
- The optimizer represents genuine R&D — algorithm design, edge-case handling, material property modeling. Charging for it is fair.
- Users can verify the calculator works, trust the science, then decide if the optimizer is worth paying for.

---

## 3. Protecting the Optimizer

### Technical Measures

| Measure | Implementation | Effectiveness |
|---------|---------------|---------------|
| **Compiled extension** | Optimizer as `.so` / `.pyd` binary | High — source code is not exposed |
| **License key validation** | Cryptographic signature check | Medium — can be bypassed by determined attackers |
| **SaaS-only for early versions** | Optimizer runs server-side only | Very High — no client code to reverse engineer |
| **Obfuscation** | Code obfuscation for Python source | Low — trivial to bypass |

**Recommended approach for launch:**
1. **Months 0–6:** Optimizer is SaaS-only. The API endpoint (`POST /api/chemistry/optimize`) is the only access point. No client-side optimizer code exists.
2. **Months 6–12:** If demand exists, release a compiled extension for self-hosted users with license key validation.
3. **Year 1+:** License key system for offline/self-hosted optimizer use.

### Legal Measures

| Measure | Cost | Effectiveness |
|---------|------|---------------|
| **Trademark "OpenGlaze"** | $250–$750 (USPTO) | High — prevents confusion, protects brand |
| **Copyright on optimizer code** | Free (automatic) | Medium — prevents literal copying |
| **Trade secret protection** | Process-based | High — if algorithm is never published |
| **Patent** | $10,000–$30,000 | Very Low — optimization heuristics are rarely patentable, and patents are public |

**Recommended:**
- Register "OpenGlaze" trademark once revenue justifies it
- Keep optimizer as trade secret (don't publish source)
- Do NOT patent — expensive, public, and antagonistic to open source community

---

## 4. What About the MIT License?

### The Honest Legal Reality

The MIT license on `openglaze-core` means:
- ✅ Anyone can use, modify, distribute the calculator code
- ✅ Anyone can sell a product built on the calculator
- ✅ Anyone can fork it and not contribute back
- ❌ MIT does NOT grant rights to the optimizer (it's not under MIT)
- ❌ MIT does NOT grant trademark rights ("OpenGlaze" is protected separately)

This is by design. The calculator is a gift to the ceramics community. The optimizer is a product.

### If Someone Forks and Competes

**Scenario:** A developer forks `openglaze-core`, builds their own optimizer, and sells it cheaper.

**Response:**
1. That's allowed. The calculator is MIT.
2. Their optimizer is their own code. You can't stop this.
3. Your advantages: first-mover, brand trust, continuous development, user base.
4. If they undercut you on price, compete on algorithm quality and support.

**This is a healthy competitive dynamic.** It keeps you honest and keeps the product improving.

---

## 5. The Actual Moats (Non-Legal)

Legal protection is secondary. Your real defenses are:

### 1. Algorithm Quality

A competitor can build an optimizer. But:
- Do they handle the no-alumina guard correctly?
- Do they know to check CTE compatibility before suggesting surface changes?
- Do they model material substitutions with accurate oxide contributions?
- Do they handle edge cases like single-material recipes, unknown materials, already-at-target recipes?

Your moat is **domain expertise encoded in the algorithm**. This takes time to replicate.

### 2. Continuous Improvement

| | Official | Fork |
|---|----------|------|
| Material database updates | Monthly (new materials, corrected properties) | Stale |
| Algorithm refinements | Based on user feedback and test results | Copied from upstream |
| New features | Roadmap-driven | Reactive |
| Bug fixes | 24–48 hours | Unknown |

### 3. Integration and Ecosystem

- Export formats that match studio workflows
- API that integrates with kiln controllers, inventory systems
- Partnerships with ceramic suppliers for material data
- Community trust in the accuracy of calculations

### 4. The SaaS Convenience Gap

Most potters are not developers. Self-hosting requires:
- Python knowledge
- Server administration
- Database setup
- Security patching

Your hosted SaaS is the path of least resistance for 90%+ of users.

---

## 6. Practical Checklist

### Now

- [ ] **Secure GitHub org and domain** — `openglaze` namespace
- [ ] **Add `TRADEMARK.md`** — "OpenGlaze" is a trademark; code is MIT
- [ ] **Separate core and optimizer** — architect the codebase for Open Core
- [ ] **Require CLAs for contributions** — Contributor License Agreement preserves relicense rights
- [ ] **Keep optimizer server-side only** for launch

### When Revenue Starts

- [ ] **Register "OpenGlaze" trademark** — USPTO filing
- [ ] **License key system** — for self-hosted optimizer access
- [ ] **Terms of Service** — for SaaS, clarifying what users get

### Never

- [ ] **BSL / SSPL / proprietary license on core** — the calculator must stay MIT
- [ ] **Patents** — expensive, public, antagonistic
- [ ] **Legal threats against forks** — MIT explicitly allows forking

---

## 7. Summary

| Question | Answer |
|----------|--------|
| **Can someone steal OpenGlaze?** | They can fork the calculator (MIT allows this). They cannot steal the optimizer without reverse engineering or reimplementing it. |
| **What's protected?** | The optimizer algorithm is proprietary. The brand is trademarked. The core calculator is open. |
| **What's the model?** | Open Core: MIT calculator + proprietary optimizer. |
| **Is this fair to users?** | Yes. The calculator uses public-domain science. The optimizer is original R&D. Users get a genuinely useful free tool and can choose to pay for advanced features. |
| **What's the real protection?** | Algorithm quality, continuous improvement, and the fact that 90% of potters won't self-host. |

---

*Document version: 2.0 — April 2026*
