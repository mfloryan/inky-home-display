#!/bin/bash

# Script to run all CI tests locally using Docker
# Matches the steps in .github/workflows/test.yml

echo "Running CI tests (Linting + Testing)..."

# Build the test image first to ensure all dependencies (like ruff) are present
docker-compose build test

# Run ruff check and pytest
docker-compose run --rm test
