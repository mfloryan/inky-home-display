.PHONY: test lint deploy

test:
	docker compose run --rm test

lint:
	uvx ruff check . --fix

deploy:
	./sync.sh
