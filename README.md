# INKY display rendering

Python script generating an INKY screen display

## Documentation

https://pillow.readthedocs.io/en/stable/reference/ImageDraw.html#functions

### SL APIs

https://www.trafiklab.se/api/sl-realtidsinformation-4

## Harwdare

## Some inspiration

https://github.com/pimoroni/inky/blob/master/examples/what/quotes-what.py

## BUILD

`docker build --pull --tag inky-display .`

`docker run --rm -v (pwd)/out:/code/img/ -v (pwd)/out/cache:/code/cache inky-display`

## DEPLOY

``
