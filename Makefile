.PHONY: run build up down lint test format precommit

run:
	PYTHONPATH=src poetry run uvicorn my_booking.main:app --reload --host 0.0.0.0 --port 9000

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

lint:
	poetry run ruff check .

format:
	poetry run ruff check . --fix

test:
	poetry run pytest -v

precommit:
	pre-commit install
