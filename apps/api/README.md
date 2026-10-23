# Vistaro API

Minimal FastAPI service created in `REPO-001`. Product modules, database
migrations, authentication, and Sentinel arrive in their own tasks.

```bash
uv sync
uv run uvicorn vistaro.main:app --reload --port 8000
```

Health check: `GET /healthz`.
