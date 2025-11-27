.PHONY: dev stop clean logs test

dev:
	docker compose up --build -d

stop:
	docker compose down

clean:
	docker compose down -v

logs:
	docker compose logs -f

test:
	docker compose exec server pytest
