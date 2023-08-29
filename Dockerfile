FROM debian:bookworm-slim
MAINTAINER Kay Hannay <klinux@hannay.de>

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY files/deploy_registry.sh /usr/bin
COPY files/create_release-0.1.0-py3-none-any.whl /tmp

RUN echo "deb http://cdn-fastly.deb.debian.org/debian bookworm main" > /etc/apt/sources.list && echo "deb http://cdn-fastly.deb.debian.org/debian bookworm-updates main" >> /etc/apt/sources.list && echo "deb http://security.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list

RUN apt update \
    && apt install -y lftp rsync apt-cacher-ng vim git live-build texlive-lang-german texlive-latex-base texlive-latex-extra texlive-latex-recommended python3-full python3-pip python3-pkgconfig docbook-to-man devscripts dpkg-dev reprepro sudo libgirepository1.0-dev libglib2.0-dev libcairo2-dev libffi-dev gir1.2-gtk-3.0 gir1.2-gudev-1.0 pipenv curl

RUN python3 -m venv /opt/create_release_venv \
    && /opt/create_release_venv/bin/pip install /tmp/create_release-0.1.0-py3-none-any.whl \
    && mkdir -p /github/home \
    && touch /github/home/.gitconfig \
    && curl -sSL https://install.python-poetry.org | python3 -

ENV PATH="/opt/create_release_venv/bin:/root/.local/bin:$PATH"

VOLUME ["/home/efalive/development"]

