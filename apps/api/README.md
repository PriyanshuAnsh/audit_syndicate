# InvestiPet API

## Run (Dev)

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test

```bash
cd apps/api
.venv/bin/pytest -q
```

## Environment Variables

- `ENVIRONMENT`: `development` or `production`
- `DEBUG`: `true` or `false`
- `JWT_SECRET`: required for production
- `DATABASE_URL`: default `sqlite:///./investipet.db`
- `CORS_ORIGINS`: comma-separated origins
- `TRUSTED_HOSTS`: comma-separated hostnames
- `ENABLE_DOCS`: expose `/docs` and `/openapi.json`
- `FORCE_HTTPS`: enable HTTPS redirect middleware

## Health Endpoints

- `GET /health`: liveness and environment info
- `GET /ready`: database connectivity check
