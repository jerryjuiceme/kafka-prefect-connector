.PHONY: help up up-demo down restart-demo install-local run-local

help:
	@echo "Available commands:"
	@echo "  make up            - Start only the Kafka-Listener service (requires external infra)"
	@echo "  make up-demo       - Start the full demo infrastructure (Kafka, Prefect, GUI, Worker, Listener)"
	@echo "  make down          - Stop and remove all containers"
	@echo "  make restart-demo  - Restart the full demo infrastructure"
	@echo "  make install-local - Install dependencies for local development (using uv)"
	@echo "  make run-local     - Run the Kafka-Listener service locally"

# Starts only the main listener service defined in docker-compose.yaml
up:
	docker-compose up -d

# Starts the listener service AND the demo infrastructure (Kafka, Zookeeper, Prefect, Worker, GUI)
up-demo:
	docker-compose -f docker-compose.yaml -f docker-compose-demo-infrastructure.yaml up -d

# Stops all containers defined in both compose files
down:
	docker-compose -f docker-compose.yaml -f docker-compose-demo-infrastructure.yaml down

# Restarts the full demo stack
restart-demo: down up-demo

# Installs dependencies using uv inside the kafka-listener directory
install-local:
	cd kafka-listener && uv sync

# Runs the application locally using uvicorn
run-local:
	cd kafka-listener && uv run uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1