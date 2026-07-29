# OpenGlaze

Free open-source ceramic glaze calculator, UMF analyzer, CTE estimator, recipe manager, and studio tool for potters and ceramic artists.

**Who it is for:** potters and ceramic studios who want local control of glaze math — not a locked SaaS calculator.

**What you get:** calculator + recipe manager you can run yourself (Docker or Python).

## Try it

```bash
git clone https://github.com/KyaniteLabs/openglaze.git
cd openglaze
cp .env.example .env   # set a real SECRET_KEY before any public exposure
docker compose up -d
curl http://localhost:8768/health
```

Or without Docker:

```bash
pip install -r requirements.txt
python seed_data.py
python server.py
```

Live tools: [openglaze.kyanitelabs.tech](https://openglaze.kyanitelabs.tech)

## Docs

- [Ceramic glaze calculator](https://openglaze.kyanitelabs.tech/ceramic-glaze-calculator.html)
- [UMF calculator](https://openglaze.kyanitelabs.tech/umf-calculator.html)
- [CTE calculator](https://openglaze.kyanitelabs.tech/cte-glaze-calculator.html)

## License

MIT. See [LICENSE](LICENSE).
