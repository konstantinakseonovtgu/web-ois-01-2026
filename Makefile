sync: deps up-d ## обновляем зависимости в .venv

deps: .venv/bin/python -m pip install -e . ## ставим зависимости

build: ## сборка образов
	docker compose build

up: ##
	docker compose up --build

up-d: ##
	docker compose up -d --build

down:
	docker compose down

stop:
	docker compose stop

restart:
	docker compose restart

ps:
	docker compose ps

exec:
	docker compose run --rm --no-deps api bash

pull:
	docker compose pull

# API

api-up:
	docker compose up -d api

# БД

bd-up:
	docker compose up -d bd

psql:
	docker compose exec db psql -U webois -d webois

db-schema:
	docker compose exec db psql -U webois -d webois -v ON_ERROR_STOP=1 -f /db/schema.sql

db-drop:
	docker compose exec db psql -U webois -d webois -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

db-seed:
	docker compose exec db psql -U webois -d webois -v ON_ERROR_STOP=1 -f /db/seed.sql

db-reset: db-drop db-schema db-seed
