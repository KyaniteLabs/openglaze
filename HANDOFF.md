# OpenGlaze Handoff

## Project Overview

OpenGlaze is a **100% open-source ceramic glaze management system** with a full stack implementation. It's designed to be self-hostable with no proprietary dependencies.

**Location:** `/Users/simongonzalezdecruz/workspaces/reverse-engineering/openglaze/`

**Port:** 8768 (intentionally different from personal instance at 8767)

---

## What's Complete

### Backend (Production-Ready)
- `server.py` - Flask REST API with all endpoints
- `auth.py` - Ory Kratos authentication integration
- `schema.sql` - PostgreSQL/SQLite schema with glazes, firings, subscriptions
- `billing/` - 4 payment provider adapters (Stripe, PayPal, BTCPay, Manual)

### Infrastructure
- `docker-compose.yml` - Full stack: Flask, Postgres, Kratos, Mailhog
- `Dockerfile` - Multi-stage build
- `kratos/config.yml` - Auth configuration (updated for port 8768)
- `kratos/identity.schema.json` - User identity schema

### Templates
- `templates/cone10-reduction-community.yaml` - 15 classic reduction glazes
- `templates/cone6-oxidation-community.yaml` - 12 electric kiln glazes

### Documentation
- `README.md` - Project overview
- `docs/installation.md` - Setup guide
- `docs/configuration.md` - Environment variables
- `docs/billing.md` - Payment provider setup

### Design System (NEW - Partially Complete)
- `static/css/design-system.css` - **Complete** modern design system with:
  - Typography: Fraunces (display) + DM Sans (body)
  - Color palette: Warm ceramic tones (celadon, tenmoku, copper)
  - Dark/light mode CSS variables
  - Components: buttons, cards, inputs, badges, avatars, navigation
  - Animations and transitions
  - Responsive breakpoints

---

## What's Remaining

### Frontend UI (Priority)
1. **Update `static/index.html`** - Replace old Glaze Lab branding with OpenGlaze, use new design system classes
2. **Update `static/css/style.css`** - Import design-system.css, remove redundant styles
3. **Update `static/js/app.js`** - Update API calls, add theme toggle functionality
4. **Create dashboard HTML** - Logged-in user experience with:
   - Glaze list view
   - Recipe editor
   - Firing log interface
   - Settings page

### Quick Wins
- Update `static/favicon.svg` with OpenGlaze branding
- Add meta tags for SEO (Open Graph, Twitter cards)
- Create 404/error pages

---

## Design Direction

**Aesthetic:** Artisan/craftsman - warm, organic, textural, celebrating handmade ceramics

**Color Inspiration:** Glaze chemistry - celadon greens, tenmoku browns, cobalt blues, copper oranges

**Key CSS Variables:**
```css
--color-primary: #5a9078 (celadon-dark)
--color-accent: #c17a4a (tenmoku-light)
--color-bg: #faf8f5 (clay-50)
--font-display: 'Fraunces'
--font-body: 'DM Sans'
```

---

## To Continue Frontend Work

```
I need to complete the OpenGlaze frontend UI.

Location: /Users/simongonzalezdecruz/workspaces/reverse-engineering/openglaze/

DONE:
- Design system CSS at static/css/design-system.css (complete)
- Backend API ready at port 8768

TODO:
1. Update static/index.html to use the new design system
2. Replace "Glaze Lab" branding with "OpenGlaze" throughout
3. Create a dashboard experience for logged-in users
4. Update static/css/style.css to import design-system.css

Read HANDOFF.md in the openglaze directory for full context.
```

---

## Key Commands

```bash
# Start the full stack
cd openglaze && docker-compose up -d

# Check service health
curl http://localhost:8768/health

# View logs
docker-compose logs -f openglaze
```

---

## File Count Summary
- Python: 8 files
- YAML config: 4 files
- Documentation: 5 files
- Frontend: 4 files (needs modernization)
- Total lines: ~3,800
