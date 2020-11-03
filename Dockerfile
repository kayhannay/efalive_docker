FROM debian:buster-slim
MAINTAINER Kay Hannay <klinux@hannay.de>

ENV DEBIAN_FRONTEND noninteractive
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN echo "deb http://ftp.de.debian.org/debian buster main" > /etc/apt/sources.list && echo "deb http://ftp.de.debian.org/debian buster-updates main" >> /etc/apt/sources.list && echo "deb http://security.debian.org buster/updates main" >> /etc/apt/sources.list

RUN apt update \
    && apt install -y apt-cacher-ng vim git live-build texlive-lang-german texlive-latex-base texlive-latex-extra texlive-latex-recommended python3 python3-pip python3-pkgconfig docbook-to-man devscripts dpkg-dev reprepro sudo libgirepository1.0-dev libglib2.0-dev libcairo2-dev libffi-dev gir1.2-gtk-3.0

RUN pip3 install pipenv

#RUN useradd -m -G sudo efalive && echo 'efalive:efalive' | chpasswd && chown efalive /home/efalive

#RUN echo "efalive ALL=NOPASSWD: /etc/init.d/apt-cacher-ng start" >> /etc/sudoers

VOLUME ["/home/efalive/development"]

#USER efalive

#WORKDIR /home/efalive

#ENV PATH "/home/efalive/.local/bin:$PATH"

#CMD /bin/bash -c "sudo /etc/init.d/apt-cacher-ng start" && /bin/bash
