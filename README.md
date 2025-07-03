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

`docker-compose run --rm inky-display-dev python src/update_display.py --png-only --output img/custom.png`

### Run tests

`docker-compose run --rm inky-display-dev python -m pytest`

## DIRECT USAGE

### On Raspberry Pi with Inky hardware (default behaviour)

`python src/update_display.py`

### On Mac/Linux with PNG output

`python src/update_display.py --png-only`

## DEPLOY

`rsync -arv --exclude '__pycache__/' src/ jagoda.mm:inky/`
