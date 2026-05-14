.PHONY: test lint deploy validate

test:
	docker compose run --rm test

lint:
	uvx ruff check . --fix

deploy:
	./sync.sh

validate:
	./validate.sh
