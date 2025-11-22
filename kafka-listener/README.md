## Start Uvicorn Server

```bash
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1
```

## Start Gunicorn Server

```bash
uv run gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
```
