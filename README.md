# TripScope

A full-stack Travel & Tourism data platform: a Python scraping/ETL pipeline, a FastAPI backend, and a React frontend for exploring destinations.

Built as a learning project to practice the complete pipeline: **scrape → clean → store → serve via API → display in a React UI → deploy.**

## Why this project

Hotel/flight aggregator sites are heavily anti-scraping and their ToS forbid it. This project instead scrapes **Wikivoyage** (openly licensed, scraping-friendly, `robots.txt`-respecting) for destination info, and is designed to be extended with real APIs (OpenWeatherMap, OpenTripMap) for weather and points of interest.

## Tech stack

- **Scraper/ETL**: Python, `requests`, `BeautifulSoup`, `pandas`
- **Backend**: FastAPI, SQLAlchemy, JWT auth (`python-jose`, `passlib`), SQLite (dev) / PostgreSQL (prod)
- **Frontend**: React (Vite), React Router, Axios, Tailwind CSS
- **Deployment**: Docker, Render/Railway (API + DB), Vercel (frontend)

## Project structure

```
travel-project/
├── scraper/       # Wikivoyage scraper + Pandas cleaning script
├── database/       # SQLAlchemy models, session setup, seed script
├── api/             # FastAPI app: routes, schemas, auth
├── frontend/         # React (Vite) app
├── docs/             # architecture/ER diagrams (add your own)
├── tests/             # pytest suite for the API
├── scripts/           # run_pipeline.py — orchestrates scraper -> clean -> seed
└── docker/             # Dockerfile + docker-compose for local Postgres + API
```

## Quickstart (local dev)

### 1. Backend + data pipeline

```bash
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r api/requirements.txt

cp .env.example .env   # defaults to local SQLite, no setup needed

# Run the pipeline: scrape -> clean -> seed the database
python scripts/run_pipeline.py

# Start the API
uvicorn api.main:app --reload
```

API docs (Swagger): http://localhost:8000/docs

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env   # points at http://localhost:8000 by default
npm run dev
```

App runs at http://localhost:5173

### 3. Tests

```bash
pip install pytest httpx
PYTHONPATH=. pytest tests/ -v
```

## Running with Docker (Postgres + API)

```bash
cd docker
docker compose up --build
```

This starts Postgres and the API together. Run the pipeline separately against that database by setting `DATABASE_URL` in your shell before running `scripts/run_pipeline.py`.

## What's implemented vs. left as extensions

**Implemented and tested end-to-end:**
- Wikivoyage scraper with `robots.txt` checks, rate limiting, retries
- Pandas cleaning: dedup, missing values, standardization, feature engineering
- Normalized SQLAlchemy schema (countries, destinations, attractions, weather_snapshots, users, favorites)
- FastAPI CRUD with pagination, search, sorting, JWT auth, Swagger docs
- React frontend: search/browse, destination detail, favorites, login/signup, dark mode
- pytest suite (6 passing tests) covering core API behavior


- Live weather/POI API integration (OpenWeatherMap, OpenTripMap) — the `weather_snapshots` table and a stub endpoint pattern are already in place
- APScheduler-based automatic re-scraping on a schedule
- Interactive map (Leaflet is installed in `frontend/package.json`, ready to wire up)
- CI/CD pipeline (GitHub Actions running `pytest` + frontend build on push)

