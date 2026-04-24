# Vessel Anatomy Taxonomy

**Source:** Ceramics terminology research from myartlesson.com, The Spruce, Gotheborg.com, Ceramic Arts Network
**Last Updated:** 2026-03-15

---

## Vessel Parts

Standard vocabulary taught in ceramics courses for vessel parts.

| Part | Definition |
|------|------------|
| **Mouth** | Top opening of a round ware such as a bowl, jar or vase |
| **Lip** | The rim or outside edge of the mouth |
| **Neck** | The narrow part of the vessel between the shoulder and lip |
| **Shoulder** | Outward curve of a vase under the neck or mouth |
| **Body** | The main, usually largest part of a vessel, part that holds the vessel's contents |
| **Foot** | The bottom projection of the vessel upon which it stands |
| **Waist** | Decorative inward curve on the body |
| **Handle** | A projection by which a vessel is held or carried |

---

## Critical Vessel Form Distinctions

### Bud Vase vs. Standard Vase

**Source:** The Spruce - "19 Types of Vases"

| Characteristic | Bud Vase | Standard Vase |
|----------------|----------|---------------|
| **Purpose** | Single flower stem only | Multiple flowers/arrangements |
| **Size** | Smallest vase category | Larger than bud vases |
| **Neck** | Typically narrow for 1-2 stems | Wider opening for multiple stems |
| **Height** | Usually under 6-8" | 6"+ typically |
| **Use Case** | Nightstand, desk, bookshelf | Table centerpiece, floor display |

**Decision Tree:**
```
Is opening narrow (holds 1-2 stems)?
├─ Yes → Is height < 6-8"?
│   ├─ Yes → BUD VASE
│   └─ No → Is body proportionally small?
│       ├─ Yes → BUD VASE
│       └─ No → VASE (narrow neck variety)
└─ No → VASE
```

### Jar vs. Bowl

**Source:** Gotheborg.com

| Characteristic | Jar | Bowl |
|----------------|-----|------|
| **Opening** | Narrower than body | Wider than or equal to body width |
| **Lip** | Constricted (even without lid present) | Open, accessible |
| **Depth** | Can be deep | Typically less than width |
| **Primary Use** | Storage-oriented form | Serving, display |

**Decision Tree:**
```
Is the opening narrower than the widest part of the body?
├─ Yes → JAR (constricted lip)
└─ No → BOWL (open form)
```

---

## Other Vessel Forms

**Source:** Gotheborg.com

| Term | Definition |
|------|------------|
| **Beaker** | Trumpet-shaped vase, no handle/spout |
| **Bottle** | Vase with spheroidal body, long neck, narrow mouth |
| **Pot** | Round, deep vessel; often with handle |
| **Saucer** | Original plate form - always saucer-shaped |
| **Basket** | Bowl with a handle across the top |
| **Effigy** | Pottery with human or animal shape |

---

## Body Profiles

Standard anatomical terms for vessel shapes.

**Source:** myartlesson.com (Ceramics Education)

| Profile | Description |
|---------|-------------|
| **Cylindrical** | Straight parallel sides |
| **Spherical** | Ball-shaped |
| **Ovoid** | Egg-shaped |
| **Conical** | Tapering to point |
| **Bell-shaped** | Flared at bottom, narrow at top |
| **Shouldered** | Distinct shoulder where body curves outward |
| **Necked** | Has a narrow neck below rim |
| **Waisted** | Narrow in middle (hourglass) |
| **Bulbous** | Round, swollen body |
| **Elongated** | Stretched tall |
| **Squat** | Short and wide |

---

## Rim Treatments

Terms describing rim/lip edge treatments.

**Source:** myartlesson.com (Ceramics Education)

| Treatment | Description |
|-----------|-------------|
| **Flared** | Widens at rim |
| **Tapered** | Narrows gradually |
| **Rolled** | Thickened rolled rim |
| **Rounded** | Soft rounded edge |
| **Squared** | Sharp 90-degree edge |

---

## Foot Types

Terms describing base/foot configurations.

**Source:** myartlesson.com (Ceramics Education)

| Type | Description |
|------|-------------|
| **Footed** | Has distinct foot ring |
| **Trimmed** | Trimmed foot (done at leather-hard stage) |
| **Flat base** | Sits flat without foot ring |

---

## Implementation Notes

These taxonomies are used for:

- **VISION_PROMPT_TEMPLATE** - piece_type detection
- **Caption generation** - accurate form descriptions
- **Hashtag selection** - form-specific tags

---

## Sources Cited

1. myartlesson.com - "Anatomy of a Clay Vessel"
2. The Spruce - "19 Types of Vases"
3. Gotheborg.com - "Names of pottery parts and shapes"
4. Ceramic Arts Network - "Glossary of Pottery Terms"
