.PHONY: dev stop clean logs test tests run

dev:
	docker compose up --build -d

stop:
	docker compose down

clean:
	docker compose down -v

logs:
	docker compose logs -f

test:
	docker compose exec chat_server pytest

tests: test

run:
	docker compose up -d
