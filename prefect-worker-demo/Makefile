.PHONY: run create-pool redeploy start-worker

run:
	export PREFECT_API_URL=http://127.0.0.1:4200/api  
	export PREFECT_API_AUTH_STRING="admin:pass"
	prefect work-pool create 'basic-pipe' --type process --overwrite
	uv run deploy.py
	prefect worker start --pool 'basic-pipe'

create-pool:
	export PREFECT_API_URL=http://127.0.0.1:4200/api  
	export PREFECT_API_AUTH_STRING="admin:pass"
	prefect work-pool create 'basic-pipe' --type process

redeploy:
	export PREFECT_API_URL=http://127.0.0.1:4200/api  
	export PREFECT_API_AUTH_STRING="admin:pass"
	uv run deploy.py

start-worker:
	export PREFECT_API_URL=http://127.0.0.1:4200/api  
	export PREFECT_API_AUTH_STRING="admin:pass"
	prefect worker start --pool 'basic-pipe'
