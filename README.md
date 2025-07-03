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

## BUILD

`docker build --pull --tag inky-display .`

`docker run --rm -v (pwd)/src:/code/src -v (pwd)/out:/code/img/ -v (pwd)/out/cache:/code/cache inky-display`

## RUN OPTIONS

### Force PNG output (skip Inky hardware detection)
`docker run --rm -v (pwd)/src:/code/src -v (pwd)/out:/code/img/ -v (pwd)/out/cache:/code/cache inky-display python src/update_display.py --png-only`

### Custom output filename
`docker run --rm -v (pwd)/src:/code/src -v (pwd)/out:/code/img/ -v (pwd)/out/cache:/code/cache inky-display python src/update_display.py --png-only --output img/my-display.png`

### On Raspberry Pi with Inky hardware (default behavior)
`python src/update_display.py`

## DEPLOY

`rsync -arv --exclude '__pycache__/' src/ jagoda.mm:inky/`
