# InvestiPet MVP

Monorepo containing:
- `apps/api`: FastAPI + SQLite backend
- `apps/web`: Next.js + Tailwind frontend
- `infra/docker-compose.yml`: local development stack
- `infra/docker-compose.prod.yml`: production-like container stack

## Local Development

1. Start backend:
```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Start frontend:
```bash
cd apps/web
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

3. Open `http://localhost:3000`

## Production-like Run (Docker)

1. Create env file from examples:
```bash
cp infra/api.env.example infra/.api.env
cp infra/web.env.example infra/.web.env
```

2. Start stack:
```bash
cd infra
docker compose -f docker-compose.prod.yml --env-file .api.env --env-file .web.env up --build
```

3. Service endpoints:
- Web: `http://localhost:3000`
- API health: `http://localhost:8000/health`
- API readiness: `http://localhost:8000/ready`

## Security/Operational Defaults Added
- Configurable CORS (`CORS_ORIGINS`) and trusted hosts (`TRUSTED_HOSTS`)
- Optional HTTPS redirect (`FORCE_HTTPS`)
- GZip compression middleware
- Docs can be disabled in production (`ENABLE_DOCS=false`)
- Refresh token expiry enforcement and rotation
- Request IDs returned in `x-request-id` response header
- Configurable live quote mode via Finnhub (`PRICE_MODE`, `FINNHUB_API_KEY`)

## Implemented API Endpoints
- Auth: register/login/refresh
- User/Pet: me, pet, family, equip
- Market: assets, quotes
- Trading: buy, sell, portfolio
- Learning: lessons list/detail/submit
- Economy: rewards balance/history, shop items, purchase, inventory
