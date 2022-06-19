# set base image (host OS)
FROM python:3-slim-buster

RUN apt-get update && apt-get install -y \
    gcc \
    fontconfig \
    locales \
    && rm -rf /var/lib/apt/lists/*

# set the working directory in the container
WORKDIR /code

# copy the dependencies file to the working directory
COPY requirements.txt .

# install dependencies
RUN pip install -r requirements.txt

# add fonts (here to optimise docker build when adding fonts)
# List of all Arch fonts https://wiki.alpinelinux.org/wiki/Fonts

RUN sed -i -e's/ main/ main non-free/g' /etc/apt/sources.list

RUN apt-get update && apt-get install -y \
    xfonts-terminus \
    fonts-ubuntu \
    fonts-roboto \
    fonts-oxygen \
    && rm -rf /var/lib/apt/lists/*

RUN fc-cache -fv
RUN fc-list
RUN gzip -d /usr/share/fonts/X11/misc/*.gz

RUN "/usr/local/bin/pilfont.py" "/usr/share/fonts/X11/misc/ter-*_iso-8859-1.pcf"
RUN "/usr/local/bin/pilfont.py" "/usr/share/fonts/X11/misc/ter-*_unicode.pcf"
#RUN "/usr/local/bin/pilfont.py" "/usr/share/fonts/misc/*x?.pcf"

COPY locale.gen /etc/locale.gen
RUN locale-gen

ENV TZ=Europe/Stockholm

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# copy the content of the local src directory to the working directory
COPY src/ .

RUN mkdir img/
VOLUME [ "/code/img" ]

# command to run on container start
CMD [ "python", "./update_display.py" ]
