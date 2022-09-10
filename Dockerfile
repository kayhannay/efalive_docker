FROM debian:bullseye-slim
MAINTAINER Kay Hannay <klinux@hannay.de>

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

COPY files/deploy_registry.sh /usr/bin
COPY files/create_release-0.1.0-py3-none-any.whl /tmp

RUN echo "deb http://cdn-fastly.deb.debian.org/debian bullseye main" > /etc/apt/sources.list && echo "deb http://cdn-fastly.deb.debian.org/debian bullseye-updates main" >> /etc/apt/sources.list && echo "deb http://security.debian.org bullseye/updates main" >> /etc/apt/sources.list

RUN apt update \
    && apt install -y lftp rsync apt-cacher-ng vim git live-build texlive-lang-german texlive-latex-base texlive-latex-extra texlive-latex-recommended python3 python3-pip python3-pkgconfig docbook-to-man devscripts dpkg-dev reprepro sudo libgirepository1.0-dev libglib2.0-dev libcairo2-dev libffi-dev gir1.2-gtk-3.0 gir1.2-gudev-1.0

RUN pip3 install pipenv poetry /tmp/create_release-0.1.0-py3-none-any.whl

VOLUME ["/home/efalive/development"]

