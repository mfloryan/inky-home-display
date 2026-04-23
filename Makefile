.PHONY: test lint deploy

test:
	docker compose run --rm test

lint:
	uv run ruff check . --fix

deploy:
	./sync.sh
