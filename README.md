# OpenGlaze

**Professional ceramic glaze management system. 100% open source.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue)](https://www.docker.com/)

## Features

- 🎨 **Unlimited Glazes** - Store and organize your entire glaze collection
- 🔥 **Firing Logs** - Document every firing with detailed notes
- 📸 **Photo Documentation** - Track results across multiple firings
- 🧮 **Recipe Calculator** - Auto-calculate batch sizes and conversions
- 📊 **Analytics** - Visualize your glaze development over time
- 👥 **Team Collaboration** - Share with studio members (Pro+)
- 💳 **Flexible Billing** - Stripe, PayPal, crypto, or manual invoicing
- 🔐 **Self-Hostable** - Run your own instance, own your data

## Quick Start

### Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/openglaze/openglaze.git
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

# Set up database
python -c "import server; server.init_db()"

# Run
python server.py
```

## Tech Stack

| Component | Technology | License |
|-----------|------------|---------|
| Backend | Flask (Python) | MIT |
| Frontend | HTML/CSS/JS (vanilla) | MIT |
| Auth | Ory Kratos | Apache 2.0 |
| Database | SQLite / PostgreSQL | Public Domain / PostgreSQL |
| Billing | Stripe, PayPal, BTCPay | MIT adapter |

## Documentation

- [Installation Guide](docs/installation.md)
- [Configuration](docs/configuration.md)
- [Template Creation](templates/README.md)
- [Billing Setup](docs/billing.md)

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
- **University Curriculum (Premium)** - Complete curriculum for ceramics programs

See [templates/](templates/) for all available templates.

## Contributing

We welcome contributions!

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

See [docs/contributing.md](docs/contributing.md) for guidelines.

## License

- **Code**: [MIT License](LICENSE) - Free to use, modify, distribute
- **Templates**: [CC-BY-4.0](templates/README.md#licensing) - Free with attribution
- **Documentation**: [CC-BY-4.0](docs/)

## Community

- **GitHub Issues**: Bug reports and feature requests
- **Discord**: [Join our community](https://discord.gg/openglaze)

## Support

- **Free tier**: Community support via GitHub Issues
- **Pro/Studio**: Priority email support
- **Education**: Dedicated support contact

For enterprise support or custom development, contact [enterprise@openglaze.app](mailto:enterprise@openglaze.app).

## Acknowledgments

Glaze recipes in our templates are sourced from the ceramics community. We credit original sources where known and encourage contributors to do the same.

---

**Built with ❤️ for the ceramics community**
