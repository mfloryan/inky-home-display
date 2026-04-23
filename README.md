# INKY display rendering

## Project Overview

Inky Home Display is a Python-based home automation dashboard that renders energy prices, weather forecasts, and public transport information to a Pimoroni Inky wHat e-paper display (400x300 pixels). The screen is updated only once every 15–60 minutes. The application integrates with Tibber (Swedish energy provider), OpenWeather API, and Stockholm public transport (SL) to create a smart home information panel.

## Reference Documentation

- [Pillow](https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#functions)
- [SL APIs](https://www.trafiklab.se/api/sl-realtidsinformation-4)

## Some inspiration

<https://github.com/pimoroni/inky/blob/master/examples/what/quotes-what.py>

## Development

### Linting

```bash
uv run ruff check . --fix
```

### Testing

Using `pytest` to execute test. Unit tests can be run locally (eg. on a Mac) but end-to-end test require docker environment, these tests are marked as `manual`.

```bash
uv run pytest
```

**TODO**: Widget tests currently fail on Mac due to font dependencies. Need to mock font loading or run widget tests in Docker.

### Visual Regression Testing

```bash
# Generate baseline images (run once or when display output changes)
./test-visual-regression.sh gen

# Run visual regression tests (default)
./test-visual-regression.sh

# Run visual regression tests explicitly
./test-visual-regression.sh test
```

Visual regression tests compare generated display images with baseline images to detect unintended changes. Failed tests generate diff images in `out/test-results/` showing highlighted differences.

## Docker Development

The code requires locale data, unix fonts and `inky` library not available on a Mac. Hence some development uses **docker** to run the code fully.

```bash
# Build once
docker compose build

# Run with PNG output (default)
docker compose run --rm inky-display

# Run with custom options
docker compose run --rm inky-display-dev uv run src/update_display.py --png-only --output out/custom.png

# Run tests in docker (linting, unit tests, and visual regression)
docker compose run --rm test
```

### Direct Usage

```bash
# On Mac/Linux with PNG output
uv run src/update_display.py --png-only
```

### Deployment

Deploy to the server using the sync script:

```bash
./sync.sh
```

This syncs `pyproject.toml` to `jagoda.mm:/opt/home-display/` and `src/` to `jagoda.mm:/opt/home-display/inky/`.

The server runs a plain Python venv at `/opt/home-display/python-env/`. The Pi Zero W is ARMv6 and cannot compile packages from source, so dependencies are installed via pip using [piwheels](https://www.piwheels.org) which provides pre-built ARM wheels.

When dependencies change, install them on the server:

```bash
uv export --no-dev -o requirements-deploy.txt
scp requirements-deploy.txt jagoda.mm:/opt/home-display/
ssh jagoda.mm '/opt/home-display/python-env/bin/pip install -r /opt/home-display/requirements-deploy.txt --extra-index-url https://www.piwheels.org/simple'
```
