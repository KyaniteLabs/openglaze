# OpenGlaze

> Screenshots needed — see [docs/screenshots/README.md](docs/screenshots/README.md) for capture instructions.

## Try it

```bash
# Clone the repository
git clone https://github.com/KyaniteLabs/openglaze.git
cd openglaze
# Copy environment file and set a real SECRET_KEY before public use
cp .env.example .env
# Start OpenGlaze
docker compose up -d
# Access at http://localhost:8768
curl http://localhost:8768/health
```

```bash
# Install dependencies
pip install -r requirements.txt
# Set up database and seed with community glazes
python seed_data.py
# Run
python server.py
```

## Docs

- [docs/screenshots/README.md](docs/screenshots/README.md)
- [Ceramic glaze calculator](https://openglaze.kyanitelabs.tech/ceramic-glaze-calculator.html)
- [UMF calculator](https://openglaze.kyanitelabs.tech/umf-calculator.html)
- [CTE calculator](https://openglaze.kyanitelabs.tech/cte-glaze-calculator.html)
- [Glazy companion](https://openglaze.kyanitelabs.tech/glazy-alternative.html)

## License

See [LICENSE](LICENSE).
