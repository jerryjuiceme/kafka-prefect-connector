# Makefile

# --- Docker Configuration ---
IMAGE_NAME := gradio-kafka-sender
IMAGE_TAG := latest

# --- Commands ---

.PHONY: help run-local docker-build docker-run docker-stop

help:
	@echo "Available commands:"
	@echo "  run-local      - Run the Gradio application locally using Python"
	@echo "  docker-build   - Build the Docker image for the application"
	@echo "  docker-run     - Run the application inside a Docker container"
	@echo "  docker-stop    - Stop and remove the running Docker container"


run-local:
	@echo ">>> Running Gradio application locally on http://127.0.0.1:7860"
	@uv run run.py

docker-build:
	@echo ">>> Building Docker image: $(IMAGE_NAME):$(IMAGE_TAG)"
	@docker build -t $(IMAGE_NAME):$(IMAGE_TAG) .

docker-run:
	@echo ">>> Running Docker container '$(IMAGE_NAME)'"
	@docker run --rm -d \
		--name $(IMAGE_NAME) \
		-p 7860:7860 \
		--env-file .env \
		$(IMAGE_NAME):$(IMAGE_TAG)
	@echo ">>> Application is running at http://localhost:7860"


docker-stop:
	@echo ">>> Stopping and removing container '$(IMAGE_NAME)'"
	@docker stop $(IMAGE_NAME) || true
	@docker rm $(IMAGE_NAME) || true