.PHONY: up down api web migrate

up:
	docker compose up --build

down:
	docker compose down

api:
	cd apps/api && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

web:
	cd apps/web && npm run dev

migrate:
	cd apps/api && alembic -c alembic.ini upgrade head
