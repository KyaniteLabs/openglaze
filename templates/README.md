# Glaze Templates

Templates are pre-built glaze collections that users can apply to their account.

## Template Format

```yaml
id: unique-template-id
name: Template Display Name
version: 1.0.0
author: Your Name
license: MIT
premium: false  # reserved; this repository ships no premium templates

description: |
  Template description goes here.
  Can span multiple lines.

tags:
  - cone10
  - reduction

glazes:
  - name: Glaze Name
    cone: "10"
    atmosphere: reduction
    base_type: glossy
    surface: smooth
    color: blue
    transparency: transparent
    notes: |
      Notes about the glaze.
      Multiple lines supported.
    recipe:
      - ingredient: Feldspar
        amount: 40
        unit: "%"
      - ingredient: Silica
        amount: 25
        unit: "%"
```

## Fields

### Template Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `id` | string | Yes | Unique identifier (URL-safe) |
| `name` | string | Yes | Display name |
| `version` | string | Yes | Semantic version |
| `author` | string | Yes | Creator name |
| `license` | string | Yes | SPDX identifier; templates here are MIT |
| `premium` | boolean | No | Is this a paid template? |
| `description` | string | Yes | Template description |
| `tags` | list | No | Tags for search/filtering |
| `glazes` | list | Yes | List of glazes |

### Glaze Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Glaze name |
| `cone` | string | Yes | Firing cone (e.g., "10", "6") |
| `atmosphere` | string | Yes | oxidation, reduction, neutral, salt, wood |
| `base_type` | string | Yes | transparent, opaque, matte, satin, gloss |
| `surface` | string | No | smooth, textured, crystalline, runny |
| `color` | string | Yes | Primary color |
| `transparency` | string | No | transparent, semi-opaque, opaque |
| `notes` | string | No | Application notes, tips |
| `recipe` | list | Yes | List of ingredients |

### Recipe Ingredient Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `ingredient` | string | Yes | Ingredient name |
| `amount` | number | Yes | Quantity |
| `unit` | string | Yes | Unit (% preferred) |

## Licensing

Every template in this repository is released under the [MIT License](../LICENSE),
the same terms as the rest of OpenGlaze. Use `license: MIT` in the template
metadata.

Premium templates are not part of this open-source repository. If a premium
collection is ever offered, it ships with its own terms and its own license
text — nothing here grants or implies those terms today.

## Contributing

1. Fork the repository
2. Add your template to `templates/`
3. Test with `python -c "import yaml; yaml.safe_load(open('templates/your-template.yaml'))"`
4. Submit a pull request

## Community Guidelines

- Test all recipes before submitting
- Include clear application notes
- Credit original sources
- Use standard ingredient names
- Specify cone accurately
