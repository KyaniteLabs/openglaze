# GlazeLab

**Professional ceramic glaze management system. 100% open source.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## Features

- 🎨 **Unlimited Glazes** — Store and organize your entire glaze collection with chemistry, recipes, and visual references
- 🔥 **Firing Logs** — Document every firing with detailed notes and atmosphere tracking
- 📸 **Photo Documentation** — Track results across multiple firings with gallery view
- 🧮 **Recipe Calculator** — Auto-calculate batch sizes, UMF, and conversions
- 🔬 **Chemistry Engine** — UMF calculation, compatibility analysis, thermal expansion, batch reporting
- 🧠 **AI Assistant (Kama)** — Context-aware glaze consulting powered by local or cloud LLMs
- 🧪 **6-Stage Experiment Pipeline** — Ideation → Prediction → Application → Firing → Analysis → Documentation
- 🎮 **Gamification** — Points, streaks, badges, and leaderboards
- 👥 **Team Collaboration** — Share with studio members (Pro+)
- 💳 **Flexible Billing** — Stripe, PayPal, crypto, or manual invoicing
- 🔐 **Self-Hostable** — Run your own instance, own your data
- 📊 **Analytics** — Visualize your glaze development over time

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/Pastorsimon1798/openglaze.git
cd openglaze

# Copy environment file
cp .env.example .env

# Start services
docker-compose up -d

# Access at http://localhost:8768
```

### Manual Installation

```bash
# Install dependencies
pip install -r requirements.txt

# Set up database and seed with default studio glazes
python seed_data.py

# Run
python server.py
```

Open http://localhost:8767 in your browser.

## Tech Stack

| Component | Technology | License |
|-----------|------------|---------|
| Backend | Flask (Python) | MIT |
| Frontend | HTML/CSS/JS (vanilla) | MIT |
| Auth | Ory Kratos | Apache 2.0 |
| Database | SQLite / PostgreSQL | Public Domain / PostgreSQL |
| Billing | Stripe, PayPal, BTCPay | MIT adapter |
| Chemistry | Custom UMF engine | MIT |
| AI | Ollama (local) / Anthropic Claude (cloud) | — |

## Architecture

```
.
├── server.py              # Flask application entry point
├── auth.py                # Authentication integration
├── schema.sql             # Unified database schema
├── config/                # Mode detection & environment config
├── core/
│   ├── schema.sql         # Database schema
│   ├── glazes/            # Glaze CRUD
│   ├── combinations/      # Layering tracking
│   ├── experiments/       # 6-stage pipeline
│   ├── chemistry/         # UMF, compatibility, batch analysis
│   ├── ai/                # Kama assistant + context retriever
│   ├── auth/              # JWT / Ory Kratos
│   ├── security/          # Rate limiting, CSP
│   ├── studios/           # Collaborative studio groups
│   ├── gamification/      # Points, streaks, badges
│   ├── predictions/       # Prediction market
│   └── simulation/        # Chemistry simulation
├── ceramics-foundation/   # Canonical ceramic data
│   ├── data/              # Structured JSON (materials, oxides, schedules)
│   ├── recipes/           # YAML recipes
│   ├── taxonomies/        # Glaze & color classifications
│   └── studios/           # Studio profile templates
├── frontend/              # Vanilla JS single-page app
├── billing/               # Payment provider router
├── kratos/                # Auth configuration
├── stages/                # 6-stage experiment pipeline docs
├── archive/               # Experiment results
├── templates/             # Shareable glaze collections
├── docs/                  # Installation, configuration, billing guides
└── scripts/               # Backup and setup utilities
```

## Data

The `ceramics-foundation/` directory contains canonical ceramic reference data:

- **30+ materials** with oxide analyses and aliases
- **19 oxides** with molecular weights, roles, and safety ratings
- **Firing schedules** for cone 06 through 10
- **UMF target ranges** and surface prediction thresholds
- **Layering rules** and material substitutions
- **Studio recipes** in YAML format

All data is versioned, sourced, and cited.

## Customizing Studio Profiles

Studio profiles live in `ceramics-foundation/studios/`. To add your own studio:

1. Copy `studios/default/` to `studios/your-studio-name/`
2. Edit `profile.json`, `clays.json`, `kilns.json`
3. Add glaze collections to `glazes/*.yaml`
4. Update `seed_data.py` or run your own seed script

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Run in debug mode
python server.py
```

## Testing

```bash
pytest tests/
```

38 tests covering:
- Kama AI context injection
- Chemistry context retrieval
- Flask route imports & streaming
- System prompt generation

## Self-Hosting

OpenGlaze is designed to be self-hosted. All components are open source and can run on your own infrastructure.

### Minimum Requirements

- 1 CPU core
- 1GB RAM
- 10GB storage
- Docker & Docker Compose

### Deployment Options

1. **VPS** (DigitalOcean, Linode, Hetzner) - $5-20/mo
2. **Managed Platform** (Render, Railway, Fly.io) - $7-25/mo
3. **Bare Metal** - Your own hardware

See [docs/installation.md](docs/installation.md) for detailed instructions.

## Pricing (Hosted Version)

| Tier | Price | Features |
|------|-------|----------|
| Free | $0 | Unlimited glazes, 50 firings/mo |
| Pro | $9/mo | Unlimited firings, analytics, 2 team members |
| Studio | $29/mo | 5 team members, custom branding, API |
| Education | $199/yr | Unlimited users, LMS integration, curriculum |

**Self-host for free** - MIT license allows unlimited use.

## Templates

Pre-built glaze collections to jumpstart your studio:

- **Cone 10 Reduction (Community)** - 15 classic reduction glazes
- **Cone 6 Oxidation (Community)** - 12 electric kiln glazes
- **Default Studio** - Configurable template for any studio

See [templates/](templates/) and [ceramics-foundation/recipes/](ceramics-foundation/recipes/) for all available collections.

## Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

- **Code**: [MIT License](LICENSE) - Free to use, modify, distribute
- **Templates**: CC-BY-4.0 - Free with attribution
- **Documentation**: CC-BY-4.0

## Community

- **GitHub Issues**: Bug reports and feature requests

## Support

- **Free tier**: Community support via GitHub Issues
- **Pro/Studio**: Priority email support
- **Education**: Dedicated support contact

---

**Built with ❤️ for the ceramics community**
