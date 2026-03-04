
.PHONY: up down clean flush-redis populate scale stress test format start scale-start

up:
	docker network create shared_network 2>/dev/null || true
	docker compose up --build -d

populate:
	docker compose -f api/docker-compose.yml --env-file .env up --build

start: up populate

MODEL_INSTANCES ?= 4

scale:
	docker network create shared_network 2>/dev/null || true
	docker compose up --build -d --scale model=$(MODEL_INSTANCES)

scale-start: scale populate

down:
	docker compose down

flush-redis:
	docker exec $$(docker ps -qf "name=redis") redis-cli FLUSHALL 2>/dev/null || true
	rm -rf uploads/*

clean: flush-redis
	docker compose down -v --remove-orphans

stress:
	cd stress_test && locust -f locustfile.py --host http://localhost:8000

test:
	pytest tests/

format:
	black .
	isort . --recursive --profile black