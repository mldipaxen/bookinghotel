ifeq ($(OS),Windows_NT)
	SLEEP := timeout

else
	SLEEP := sleep
endif

# dev

start:
	docker compose -f docker-compose.yaml up --build -d

update-api:
	docker compose -f docker-compose.yaml exec -w /core api rm -r src
	docker compose -f docker-compose.yaml cp ./api/src api:core

update-db:
	docker compose -f docker-compose.yaml exec -w /core api python -m alembic upgrade head

update-pkgs:
	docker compose -f docker-compose.yaml cp ./api/requirements.txt api:/core
	docker compose -f docker-compose.yaml exec -w /core api pip install -r requirements.txt
	docker compose -f docker-compose.yaml restart api

new-migr:
	docker compose -f docker-compose.yaml cp ./api/src/database api:/core/src
	docker compose -f docker-compose.yaml exec -w /core api python -m alembic revision --autogenerate -m "$(name)"
	docker compose -f docker-compose.yaml cp api:/core/src/migrations/versions ./api/src/migrations
	docker compose -f docker-compose.yaml exec -w /core api python -m alembic upgrade head

see-db:
	docker compose -f docker-compose.yaml exec database psql -U postgres

see-api:
	docker compose -f docker-compose.yaml logs -f api --since $(time)

gen-dump:
	docker compose -f docker-compose.yaml exec database sh -c 'pg_dump -h 127.0.0.1 --username=postgres -d postgres > dumps/$$(date +'%Y-%m-%d_%H-%M-%S').dump'

stop:
	docker compose -f docker-compose.yaml down