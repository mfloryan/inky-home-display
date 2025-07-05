# INKY display rendering

Python script generating an INKY screen display

## Documentation

<https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#functions>

### SL APIs

<https://www.trafiklab.se/api/sl-realtidsinformation-4>

## Hardware

## Some inspiration

<https://github.com/pimoroni/inky/blob/master/examples/what/quotes-what.py>

## Lint

`ruff check . --fix`

## DOCKER DEVELOPMENT

### Build once

`docker-compose build`

### Run with PNG output (default)

`docker-compose run --rm inky-display`

### Run with custom options

`docker-compose run --rm inky-display-dev python src/update_display.py --png-only --output out/custom.png`

### Run tests

`docker-compose run --rm inky-display-dev python -m pytest`

### Visual regression testing

```bash
# Generate baseline images (run once or when display output changes)
./test-visual-regression.sh gen

# Run visual regression tests (default)
./test-visual-regression.sh

# Run visual regression tests explicitly
./test-visual-regression.sh test
```

Visual regression tests compare generated display images with baseline images to detect unintended changes. Failed tests generate diff images in `out/test-results/` showing highlighted differences.

## DIRECT USAGE

### On Raspberry Pi with Inky hardware (default behaviour)

`python src/update_display.py`

### On Mac/Linux with PNG output

`python src/update_display.py --png-only`

## DEPLOY

`rsync -arv --exclude '__pycache__/' src/ jagoda.mm:inky/`
