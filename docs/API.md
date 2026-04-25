# OpenGlaze API Reference

Complete reference for the OpenGlaze REST API.

**Base URL**: `https://your-instance.com/api`

**Authentication**: Bearer token (JWT) or session cookie

## Authentication

### Login

```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password"
}
```

**Response:**

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "id": 1,
    "email": "user@example.com",
    "name": "Jane Potter"
  }
}
```

### Register

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure-password",
  "name": "Jane Potter"
}
```

## Glazes

### List Glazes

```http
GET /api/glazes?page=1&per_page=20&search=celadon&cone=10&atmosphere=reduction
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `page` | integer | Page number (default: 1) |
| `per_page` | integer | Items per page (default: 20, max: 100) |
| `search` | string | Search by name, family, or description |
| `cone` | string | Filter by cone (e.g., "10", "6", "06") |
| `atmosphere` | string | Filter by atmosphere (oxidation, reduction, neutral) |
| `base_type` | string | Filter by base type |
| `surface` | string | Filter by surface finish |

**Response:**

```json
{
  "glazes": [
    {
      "id": 1,
      "name": "Celadon",
      "family": "celadon",
      "hex": "#8FBC8F",
      "chemistry": "SiO2: 2.8, Al2O3: 0.4, CaO: 0.6...",
      "recipe": "Feldspar: 45%, Silica: 30%, Whiting: 15%...",
      "cone": "10",
      "atmosphere": "reduction",
      "food_safe": true,
      "base_type": "stoneware",
      "surface": "glossy",
      "transparency": "semi-transparent",
      "created_at": "2026-04-01T12:00:00Z"
    }
  ],
  "total": 45,
  "page": 1,
  "per_page": 20
}
```

### Get Glaze by ID

Glaze IDs are string slugs (e.g., `celadon`, `tenmoku`), not integers.

```http
GET /api/glazes/<id>
Authorization: Bearer <token>
```

### Create Glaze

```http
POST /api/glazes
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "My Custom Glaze",
  "family": "ash",
  "recipe": "Feldspar: 50%, Silica: 30%, Ash: 20%",
  "chemistry": "SiO2: 3.0, Al2O3: 0.5, CaO: 0.5",
  "cone": "10",
  "atmosphere": "reduction",
  "food_safe": false,
  "base_type": "stoneware",
  "surface": "matte",
  "transparency": "opaque"
}
```

### Update Glaze

```http
PUT /api/glazes/<id>
Content-Type: application/json
Authorization: Bearer <token>
```

### Delete Glaze

```http
DELETE /api/glazes/<id>
Authorization: Bearer <token>
```

## Combinations

### List Combinations

```http
GET /api/combinations?base=Tenmoku&top=Chun+Blue
Authorization: Bearer <token>
```

### Create Combination

```http
POST /api/combinations
Content-Type: application/json
Authorization: Bearer <token>

{
  "base": "Tenmoku",
  "top": "Chun Blue",
  "type": "user-prediction",
  "source": "user",
  "result": "Predicted: subtle breaking at edges",
  "risk": "low",
  "effect": "subtle"
}
```

**Types:** `research-backed`, `user-prediction`, `confirmed`, `surprise`

## Experiments

### List Experiments

```http
GET /api/experiments?stage=firing&status=active
Authorization: Bearer <token>
```

### Create Experiment

```http
POST /api/experiments
Content-Type: application/json
Authorization: Bearer <token>

{
  "title": "Copper Red Test Series",
  "glaze_id": 5,
  "stage": "ideation",
  "notes": "Testing copper carbonate percentages from 0.5% to 2%",
  "hypothesis": "1% copper will produce the best red with minimal pinholing"
}
```

### Update Experiment Stage

```http
PATCH /api/experiments/<id>
Content-Type: application/json
Authorization: Bearer <token>

{
  "stage": "firing",
  "firing_log": {
    "cone": "10",
    "atmosphere": "reduction",
    "schedule": "slow-cool",
    "temperature": 1285,
    "duration": 12
  }
}
```

## Chemistry

### Calculate UMF

```http
GET /api/glazes/<glaze_id>/umf?cone=10
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cone` | integer | Target firing cone (e.g., 6, 10). Affects limit checks and surface prediction. Defaults to 10. |

**Response:**

```json
{
  "success": true,
  "recipe_parsed": true,
  "umf_formula": {
    "SiO2": 3.2,
    "Al2O3": 0.45,
    "CaO": 0.55,
    "K2O": 0.3,
    "Na2O": 0.15
  },
  "ratios": {
    "silica_alumina": 7.11,
    "flux_alumina": 1.22
  },
  "surface_prediction": "glossy",
  "surface_confidence": "high",
  "thermal_expansion": 6.2,
  "limit_warnings": [],
  "warnings": [],
  "missing_materials": [],
  "error": null,
  "cone": 10,
  "confidence": {
    "surface": "high",
    "limits": "high",
    "overall": "high"
  },
  "recommendations": [
    "UMF looks reasonable for cone 10. Fire a test tile to confirm surface, color, and fit on your clay body."
  ],
  "glaze_id": "celadon",
  "glaze_name": "Celadon"
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether calculation succeeded |
| `recipe_parsed` | boolean | Whether the recipe was parsed without errors |
| `umf_formula` | object | Unity Molecular Formula (fluxes sum to 1.0) |
| `ratios` | object | Key ratios: `silica_alumina`, `flux_alumina` |
| `surface_prediction` | string | Predicted surface: `matte`, `satin`, `glossy` |
| `surface_confidence` | string | `high`, `medium`, `low` — how close to a boundary |
| `thermal_expansion` | float | CTE in ×10⁻⁶/°C (Appen molar method) |
| `limit_warnings` | array | UMF values outside cone-specific recommended ranges |
| `warnings` | array | General warnings |
| `missing_materials` | array | Materials that could not be resolved |
| `error` | string | Error message if `success` is false |
| `cone` | integer | Cone used for analysis |
| `confidence` | object | Per-prediction confidence: `surface`, `limits`, `overall` |
| `recommendations` | array | Actionable guidance for testing and reformulation |

### Check Compatibility

```http
GET /api/combinations/<combo_id>/compatibility?cone=10
Authorization: Bearer <token>
```

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `cone` | integer | Target firing cone (e.g., 6, 10). Affects UMF analysis for both glazes. Defaults to 10. |

**Response:**

```json
{
  "success": true,
  "compatible": true,
  "score": 0.85,
  "risk_factors": [],
  "warnings": ["Ensure both glazes are at the same maturity at target cone"],
  "recommended_order": "base then top",
  "thermal_expansion_risk": "low",
  "thermal_expansion_delta": 0.3,
  "cte_base": 6.2,
  "cte_top": 6.5,
  "fluidity_interaction": "similar",
  "oxide_interactions": [],
  "base_umf": {...},
  "top_umf": {...},
  "cone": 10,
  "test_recommendations": [
    "High compatibility score (0.85). This combination looks promising. Fire a test tile at cone 10 to confirm color and surface.",
    "Fire test tile to cone 10 with your standard schedule. Use witness cones to verify actual temperature."
  ],
  "risk_breakdown": []
}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `success` | boolean | Whether analysis succeeded |
| `compatible` | boolean | Whether the combination is predicted compatible |
| `score` | float | Compatibility score 0.0–1.0 (higher = better) |
| `risk_factors` | array | Named risk factors |
| `warnings` | array | Advisory warnings |
| `recommended_order` | string | Suggested layering order |
| `thermal_expansion_risk` | string | `low`, `medium`, `high`, or `unknown` |
| `thermal_expansion_delta` | float | Absolute CTE difference in ×10⁻⁶/°C |
| `cte_base` | float | Base glaze CTE in ×10⁻⁶/°C |
| `cte_top` | float | Top glaze CTE in ×10⁻⁶/°C |
| `fluidity_interaction` | string | Fluidity relationship description |
| `oxide_interactions` | array | Specific oxide interaction warnings |
| `base_umf` | object | Full UMF result for base glaze |
| `top_umf` | object | Full UMF result for top glaze |
| `cone` | integer | Cone used for analysis |
| `test_recommendations` | array | Specific, actionable testing guidance |
| `risk_breakdown` | array | Structured risks with severity and mitigation |

### Scale Recipe

```http
POST /api/chemistry/scale
Content-Type: application/json

{
  "recipe": "Feldspar 45, Silica 30, Whiting 15, Kaolin 10",
  "batch_size_grams": 5000
}
```

Recipe can also be passed as an object with material names as keys and percentages as values.

**Response:**

```json
{
  "success": true,
  "batch": {
    "Feldspar": 2250.00,
    "Silica": 1500.00,
    "Whiting": 750.00,
    "Kaolin": 500.00
  },
  "total_grams": 5000.00,
  "unit": "grams",
  "original_percentages": {
    "Feldspar": 45.00,
    "Silica": 30.00,
    "Whiting": 15.00,
    "Kaolin": 10.00
  }
}
```

### Batch Analysis

```http
POST /api/chemistry/batch
Content-Type: application/json

{
  "analyze_all": true
}
```

**Response:**

```json
{
  "summary": {
    "glazes": {"total": 32, "parsed": 28, "failed": 4},
    "combinations": {"total": 30, "compatible": 12, "incompatible": 15, "unknown": 3},
    "surface_distribution": {"glossy": 20, "satin": 5, "matte": 7},
    "average_compatibility_score": 0.45
  },
  "glazes": {...},
  "combinations": {...}
}
```

### Optimize Recipe

Computationally suggest exact material adjustments to hit target glaze properties without physical test firings.

```http
POST /api/chemistry/optimize
Content-Type: application/json
```

**Request:**

```json
{
  "recipe": "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12",
  "target": "more_matte",
  "max_suggestions": 5
}
```

**Targets:**

| Target | Description | `target_value` Required |
|--------|-------------|------------------------|
| `target_cte` | Match exact CTE (×10⁻⁶/°C) | Yes |
| `reduce_cte` | Lower thermal expansion | No |
| `increase_cte` | Raise thermal expansion | No |
| `more_matte` | Increase matte character | No |
| `more_glossy` | Increase gloss character | No |
| `reduce_alkali` | Lower KNaO for durability | No |
| `reduce_running` | Reduce fluidity risk | No |

**Response:**

```json
{
  "success": true,
  "original_recipe": "Custer Feldspar 45, Silica 25, Whiting 18, EPK 12",
  "target": "more_matte",
  "original_cte": 6.92,
  "original_surface": "glossy",
  "suggestions": [
    {
      "recipe": "Custer Feldspar 45.00, Whiting 18.00, EPK 37.00",
      "change_description": "Replace silica with kaolin (adds alumina, lowers CTE, more matte) (100% swap)",
      "predicted_cte": 7.46,
      "predicted_surface": "matte",
      "score": 148.4,
      "distance_from_target": 148.4
    },
    {
      "recipe": "Custer Feldspar 45.00, Silica 6.25, Whiting 18.00, EPK 30.75",
      "change_description": "Replace silica with kaolin (adds alumina, lowers CTE, more matte) (75% swap)",
      "predicted_cte": 7.31,
      "predicted_surface": "satin",
      "score": 82.2,
      "distance_from_target": 82.2
    }
  ],
  "error": null
}
```

**How it works:**

The optimizer grid-searches the adjustment space using:
- Single-material adjustments (±5/10/15/20/30%)
- Material substitutions (e.g., silica ↔ kaolin, feldspar ↔ nepheline syenite, whiting ↔ wollastonite)
- Common material additions

Each candidate is scored by distance to the target, with threshold-crossing bonuses (e.g., +50 for moving from glossy → matte territory). Results are ranked by score and deduplicated.

## AI (Kama)

### Ask Kama

```http
POST /api/ask
Content-Type: application/json
Authorization: Bearer <token>

{
  "question": "What would happen if I add 2% rutile to this celadon?",
  "glaze_context": ["celadon", "rutile-blue"],
  "stream": false
}
```

**Response:**

```json
{
  "response": "Adding 2% rutile to a celadon base would likely...",
  "sources": ["glaze_id:1", "chemistry_rules:7"],
  "confidence": "high"
}
```

### Streaming Response

```http
POST /api/ask/stream
Content-Type: application/json
Authorization: Bearer <token>

{
  "question": "Explain UMF calculation",
  "stream": true
}
```

**Response:** Server-sent events (SSE) stream.

## Studios

### List Studios

```http
GET /api/studios
Authorization: Bearer <token>
```

### Create Studio

```http
POST /api/studios
Content-Type: application/json
Authorization: Bearer <token>

{
  "name": "My Studio",
  "description": "Cone 10 gas reduction studio",
  "profile": {
    "cone": "10",
    "atmosphere": "reduction",
    "kiln_type": "gas"
  }
}
```

### Add Member

```http
POST /api/studios/<id>/members
Content-Type: application/json
Authorization: Bearer <token>

{
  "user_email": "member@example.com",
  "role": "member"
}
```

**Roles:** `owner`, `admin`, `member`, `viewer`

## Billing

### Get Subscription

```http
GET /api/billing/subscription
Authorization: Bearer <token>
```

### Create Checkout Session

```http
POST /api/billing/checkout
Content-Type: application/json
Authorization: Bearer <token>

{
  "tier": "pro",
  "interval": "monthly",
  "provider": "stripe"
}
```

**Tiers:** `free`, `pro`, `studio`, `education`
**Intervals:** `monthly`, `yearly`
**Providers:** `stripe`, `paypal`, `btcpay`, `manual`

### Webhooks

Payment providers send webhook events to:

- Stripe: `POST /api/billing/webhook/stripe`
- PayPal: `POST /api/billing/webhook/paypal`
- BTCPay: `POST /api/billing/webhook/btcpay`

## Uploads

### Upload Photo

```http
POST /api/uploads
Content-Type: multipart/form-data
Authorization: Bearer <token>

file: <binary>
glaze_id: 1
firing_id: 5
caption: "Cone 10 reduction, April 2026"
```

## Gamification

### Get User Stats

```http
GET /api/gamification/stats
Authorization: Bearer <token>
```

**Response:**

```json
{
  "points": 1250,
  "streak_days": 7,
  "total_experiments": 23,
  "badges": ["first_glaze", "ten_experiments", "streak_week"],
  "rank": "Journeyman Potter"
}
```

### Get Leaderboard

```http
GET /api/gamification/leaderboard?studio_id=1&period=month
```

## Predictions

### Create Prediction

```http
POST /api/predictions
Content-Type: application/json
Authorization: Bearer <token>

{
  "combination_id": 5,
  "prediction": "The result will be a deep blue with iron breaking",
  "confidence": 0.8
}
```

## Health

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "timestamp": "2026-04-24T11:00:00Z"
}
```

## Error Responses

All errors follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid cone value",
    "details": {
      "cone": "Must be one of: 06, 04, 02, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14"
    }
  }
}
```

**Common Error Codes:**

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | Missing or invalid token |
| `FORBIDDEN` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 422 | Invalid request data |
| `RATE_LIMITED` | 429 | Too many requests |
| `INTERNAL_ERROR` | 500 | Server error |

## Rate Limits

- Authenticated: 60 requests/minute
- Unauthenticated: 20 requests/minute
- AI endpoints: 10 requests/minute

## Pagination

List endpoints use cursor-based pagination:

```http
GET /api/glazes?page=2&per_page=50
```

**Response includes:**

```json
{
  "items": [...],
  "total": 200,
  "page": 2,
  "per_page": 50,
  "total_pages": 4,
  "has_next": true,
  "has_prev": true
}
```
