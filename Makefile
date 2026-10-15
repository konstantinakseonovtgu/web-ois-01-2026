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
	docker compose run --rm --no-deps api sh

pull:
	docker compose pull

