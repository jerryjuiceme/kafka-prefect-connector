export PREFECT_API_URL=http://127.0.0.1:4200/api  
export PREFECT_API_AUTH_STRING="admin:pass"

prefect work-pool create 'basic-pipe' --type process

uv run deploy.py

prefect worker start --pool 'basic-pipe'
