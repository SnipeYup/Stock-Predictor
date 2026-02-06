# AI Stock Prediction Platform (MVP)

A runnable MVP of a news-driven stock prediction web app built with Python standard library components (no external runtime dependencies).

## Implemented now
- Global-ready asset model and seeded starter universe.
- News article storage + ticker linkage.
- Prediction engine with multi-timeframe support (`hours`, `days`, `weeks`, `months`, `years`).
- Explicit insufficient-data output: `0% certainty – not enough data`.
- Live stock browser endpoint with sorting by ticker/performance/confidence.
- Search endpoint supporting partial matches and on-demand ticker onboarding.
- Per-stock detail endpoint with probability distribution and direct article links.
- Browser UI for list/search/detail workflows.

## Run
### macOS / Linux
```bash
python run.py
```

### Windows PowerShell
```powershell
python run.py
```

### Windows CMD
```cmd
python run.py
```

Then open `http://127.0.0.1:8000`.

## API quick checks
```bash
curl 'http://127.0.0.1:8000/stocks?sort_by=confidence'
curl -X POST 'http://127.0.0.1:8000/predict/AAPL?timeframe=days'
curl 'http://127.0.0.1:8000/stocks/AAPL?timeframe=days'
```
