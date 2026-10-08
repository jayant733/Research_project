# Makefile for Adaptive Privacy Orchestrator
# Technical Explanation: automates standard developer tooling commands.

.PHONY: setup install format lint typecheck test clean build-env demo

setup:
	python -m venv .venv
	@echo "Virtual environment created. Please activate using: .venv\\Scripts\\activate (Windows) or source .venv/bin/activate (Unix)"

install:
	pip install --upgrade pip setuptools
	pip install -e .[dev]

format:
	black .

lint:
	ruff check .

typecheck:
	mypy .

test:
	pytest tests/

check-all: format lint typecheck test

# Docker Standard Commands
# Technical Explanation: Orchestrates building, running profiles, and cleaning container workflows.

demo:
	python -m backend.demo

docker-build:
	docker build -f docker/Dockerfile.base -t adaptive-privacy-base:latest .
	docker compose build

docker-dev-up:
	docker compose --profile demo up --build

docker-benchmark-up:
	docker compose --profile benchmark up -d

docker-prod-up:
	docker compose --profile production up -d

docker-down:
	docker compose down --volumes --remove-orphans

docker-logs:
	docker compose logs -f

docker-clean: docker-down
	docker rmi adaptive-privacy-base:latest || true
	docker system prune -f --volumes

clean:
	rm -rf .venv/
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .mypy_cache/
	rm -rf .ruff_cache/
	rm -rf .pytest_cache/
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
