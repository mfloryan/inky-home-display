# set base image (host OS)
FROM python:3.13-slim-trixie

RUN apt-get update && apt-get install -y \
    gcc \
    fontconfig \
    locales \
    && rm -rf /var/lib/apt/lists/*

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY pyproject.toml uv.lock ./

# install dependencies
ARG INSTALL_DEV=false
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1

RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=cache,target=/root/.cache/uv \
    if [ "$INSTALL_DEV" = "true" ] ; then \
        uv sync --frozen --dev; \
    else \
        uv sync --frozen --no-dev; \
    fi

# add fonts (here to optimise docker build when adding fonts)
# List of all Arch fonts https://wiki.alpinelinux.org/wiki/Fonts

RUN set -eux; \
    sed -i 's/main$/main non-free/' /etc/apt/sources.list.d/debian.sources;

RUN apt-get update && apt-get install -y \
    fonts-terminus-otb \
    fonts-ubuntu \
    fonts-roboto \
    && rm -rf /var/lib/apt/lists/*

RUN fc-cache -fv
RUN fc-list

COPY locale.gen /etc/locale.gen
RUN locale-gen

ENV TZ=Europe/Stockholm

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir out/
VOLUME [ "/code/out" ]
RUN mkdir -p cache
VOLUME [ "/code/cache" ]
VOLUME [ "/code/src" ]

# command to run on container start
CMD [ "uv", "run", "src/update_display.py" ]
