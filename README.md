# OpenGlaze

<p align="center">
  <img src="frontend/favicon.svg" alt="OpenGlaze Logo" width="120">
</p>

<p align="center">
  <strong>Professional ceramic glaze management system. 100% open source.</strong>
</p>

<p align="center">
  <a href="https://github.com/Pastorsimon1798/openglaze/actions/workflows/ci.yml">
    <img src="https://github.com/Pastorsimon1798/openglaze/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <a href="https://github.com/Pastorsimon1798/openglaze/releases">
    <img src="https://img.shields.io/github/v/release/Pastorsimon1798/openglaze?include_prereleases" alt="Latest Release">
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://www.python.org/">
    <img src="https://img.shields.io/badge/Python-3.12+-blue.svg" alt="Python 3.12+">
  </a>
  <a href="https://www.docker.com/">
    <img src="https://img.shields.io/badge/Docker-Ready-blue" alt="Docker Ready">
  </a>
  <a href="https://github.com/Pastorsimon1798/openglaze/stargazers">
    <img src="https://img.shields.io/github/stars/Pastorsimon1798/openglaze" alt="GitHub Stars">
  </a>
</p>

<p align="center">
  <a href="#quick-start">Quick Start</a> •
  <a href="#features">Features</a> •
  <a href="#documentation">Docs</a> •
  <a href="#self-hosting">Self-Host</a> •
  <a href="#contributing">Contribute</a>
</p>

---

## Overview

OpenGlaze is a complete, open-source platform for ceramic artists and studios to manage glaze recipes, track firings, document experiments, and collaborate on glaze development. Built by potters, for potters.

**Why OpenGlaze?**

- 🏠 **Own your data** — Self-host on your own infrastructure
- 🔓 **Truly open** — MIT licensed, no proprietary lock-in
- 🧠 **AI-powered** — Kama assistant understands glaze chemistry
- 🎨 **Studio-ready** — Multi-user collaboration out of the box
- ☕ **Free forever** — No paywalls, no subscriptions, no feature gates

## Quick Start

### Docker (Recommended, 2 minutes)

```bash
# Clone the repository
git clone https://github.com/Pastorsimon1798/openglaze.git
cd openglaze

# Copy environment file
cp .env.example .env

# Start the full stack
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

## Features

<table>
<tr>
<td width="50%">

### 🎨 Glaze Management
- Store unlimited glazes with chemistry, recipes, and visual references
- Track family relationships and base types
- UMF calculation with automatic oxide analysis
- Recipe scaling and batch calculator
- Food safety and cone range annotations

</td>
<td width="50%">

### 🔬 Chemistry Engine
- UMF (Unity Molecular Formula) calculation
- Glaze compatibility analysis
- Thermal expansion coefficient matching
- **Recipe optimizer** — suggests exact tweaks to hit target CTE, surface, or durability
- Batch reporting with cost estimation
- Oxide analysis and substitution suggestions

</td>
</tr>
<tr>
<td width="50%">

### 🧠 AI Assistant (Kama)
- Context-aware glaze consulting
- Streaming responses for real-time help
- Local LLM support (Ollama) or cloud (Claude)
- Chemistry-aware prompt injection
- Experiment suggestion engine

</td>
<td width="50%">

### 🧪 Experiment Pipeline
- 6-stage workflow: Ideation → Prediction → Application → Firing → Analysis → Documentation
- Photo documentation at each stage
- Structured firing log integration
- Result comparison and archiving
- Reproducibility tracking

</td>
</tr>
<tr>
<td width="50%">

### 👥 Studio Collaboration
- Multi-member studio groups
- Role-based access control
- Shared glaze libraries
- Lab assignment tracking
- Comment threads on experiments

</td>
<td width="50%">

### 🎮 Gamification
- Points and streak tracking
- Achievement badges
- Activity leaderboards
- Experiment milestones
- Community challenges

</td>
</tr>
</table>

### More Features

- 🧮 **Recipe Optimizer** — Compute exact material adjustments to hit target properties without physical testing
- 📸 **Photo Documentation** — Gallery view across multiple firings
- 🔥 **Firing Logs** — Atmosphere, cone, and schedule tracking
- 🧮 **Layering Tracker** — Document and predict base/top combinations
- 💾 **Import/Export** — Glazy CSV, Digitalfire INSIGHT, YAML
- 📊 **Analytics** — Visualize glaze development over time
- 📱 **PWA** — Install as an app on mobile/desktop
- ⌨️ **Command Palette** — Quick navigation with ⌘K
- 🔐 **Auth** — Ory Kratos integration or simple local auth

## Tech Stack

| Component | Technology | License |
|-----------|------------|---------|
| Backend | Flask 3.x (Python) | MIT |
| Frontend | Vanilla JS SPA | MIT |
| Database | SQLite / PostgreSQL | Public Domain / PostgreSQL |
| Auth | Ory Kratos / JWT | Apache 2.0 |
| AI | Ollama (local) / Anthropic Claude (cloud) | — |
| Import/Export | Glazy, INSIGHT, YAML | MIT |
| Chemistry | Custom UMF Engine | MIT |
| Container | Docker + Compose | — |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Browser    │  │   PWA App    │  │   API Clients│      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                     Flask Application                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │  Glazes  │ │Chemistry │ │    AI    │ │ Templates│       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐       │
│  │ Studios  │ │   Auth   │ │Analytics │ │  Uploads │       │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘       │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────────┐  │
│  │SQLite/   │  │Ory       │  │Ceramics Foundation Data  │  │
│  │PostgreSQL│  │Kratos    │  │(Materials, Recipes, etc.)│  │
│  └──────────┘  └──────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Documentation

| Document | Description |
|----------|-------------|
| [Installation](docs/installation.md) | Docker and manual setup guides |
| [Configuration](docs/configuration.md) | Environment variables and settings |
| [API Reference](docs/API.md) | REST API endpoints and examples |
| [Architecture](docs/architecture.md) | System design and data flow |
| [User Guide](docs/user-guide.md) | End-user feature walkthrough |
| [Development](docs/development.md) | Contributing and local dev setup |
| [Self-Hosting](docs/self-hosting.md) | Production deployment guide |
| [Support](docs/support.md) | Voluntary support for the project |
| [Changelog](CHANGELOG.md) | Version history and release notes |

## Self-Hosting

OpenGlaze is designed for self-hosting. All components are open source.

### Minimum Requirements

- 1 CPU core
- 1 GB RAM
- 10 GB storage
- Docker & Docker Compose

### Deployment Options

| Platform | Cost | Difficulty | Best For |
|----------|------|------------|----------|
| VPS (Hetzner, DO, Linode) | $5-20/mo | Medium | Full control |
| Render / Railway / Fly.io | $7-25/mo | Easy | Managed platforms |
| Raspberry Pi / Bare Metal | $0 | Hard | Offline/local use |

See [docs/self-hosting.md](docs/self-hosting.md) for detailed deployment instructions for each platform.

## Support the Project

OpenGlaze is free and open source. If it saves you materials, time, or a failed kiln load, consider supporting ongoing development:

- **[Buy me a coffee](https://ko-fi.com/yourname)** *(update with your link)*
- **[Patreon](https://patreon.com/yourname)** *(update with your link)*
- **[GitHub Sponsors](https://github.com/sponsors/yourname)** *(update with your link)*

No pressure — the tool is yours either way.

## Customizing Studio Profiles

Studio profiles live in `ceramics-foundation/studios/`. To add your own:

1. Copy `studios/default/` → `studios/your-studio/`
2. Edit `profile.json`, `clays.json`, `kilns.json`
3. Add glaze collections to `glazes/*.yaml`
4. Update `seed_data.py` or create your own seed script

No code changes required — everything is data-driven.

## Data

The `ceramics-foundation/` directory contains canonical ceramic reference data:

- **30+ materials** with oxide analyses and aliases
- **19 oxides** with molecular weights, roles, and safety ratings
- **Firing schedules** for cone 06 through 10
- **UMF target ranges** and surface prediction thresholds
- **Layering rules** and material substitutions
- **Studio recipes** in YAML format

All data is versioned, sourced, and cited. See [ceramics-foundation/](ceramics-foundation/) for the full dataset.

## Templates

Pre-built glaze collections:

- **Cone 10 Reduction (Community)** — 15 classic reduction glazes
- **Cone 6 Oxidation (Community)** — 12 electric kiln glazes
- **Default Studio** — Configurable template for any studio

See [templates/](templates/) and [ceramics-foundation/recipes/](ceramics-foundation/recipes/).

## Testing

```bash
# Run the full test suite
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html
```

111 tests covering:
- Kama AI context injection and streaming
- Chemistry context retrieval and UMF calculation
- Recipe optimizer (target CTE, surface, alkali, running risk)
- Flask route imports and response formats
- System prompt generation and database schema

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

Quick start:

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/openglaze.git
cd openglaze

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest tests/

# Make changes and submit a PR
```

## Security

See [SECURITY.md](SECURITY.md) for our security policy and vulnerability reporting process.

## Support

Questions, bug reports, and feature requests:

- [GitHub Discussions](https://github.com/Pastorsimon1798/openglaze/discussions) — Community help
- [GitHub Issues](https://github.com/Pastorsimon1798/openglaze/issues) — Bug reports and feature requests

### Support the Project

OpenGlaze is free and open source under the MIT license. If this tool saved you materials, time, or a failed kiln load, consider supporting its continued development:

- [☕ Buy me a coffee on Ko-fi](https://ko-fi.com/yourname)
- [🎨 Support on Patreon](https://patreon.com/yourname)
- [⭐ Sponsor on GitHub](https://github.com/sponsors/yourname)

No pressure — the tool is yours either way.

## License

- **Code**: [MIT License](LICENSE) — Free to use, modify, distribute
- **Templates**: CC-BY-4.0 — Free with attribution
- **Documentation**: CC-BY-4.0

## Acknowledgments

- The ceramics community for sharing knowledge and recipes
- Contributors who have helped build OpenGlaze
- [Ceramic Arts Network](https://ceramicartsnetwork.org/) for glaze chemistry references
- [Digitalfire](https://digitalfire.com/) for oxide data and UMF methodology

---

<p align="center">
  <strong>Built with ❤️ for the ceramics community</strong>
</p>

<p align="center">
  <a href="https://github.com/Pastorsimon1798/openglaze">GitHub</a> •
  <a href="https://github.com/Pastorsimon1798/openglaze/discussions">Discussions</a> •
  <a href="https://openglaze.com">Website</a>
</p>
