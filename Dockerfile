FROM 32bit/debian:jessie
MAINTAINER Kay Hannay <klinux@hannay.de>

ENV DEBIAN_FRONTEND noninteractive

RUN echo "deb http://ftp.de.debian.org/debian jessie main" > /etc/apt/sources.list && echo "deb http://ftp.de.debian.org/debian jessie-updates main" >> /etc/apt/sources.list && echo "deb http://security.debian.org jessie/updates main" >> /etc/apt/sources.list

RUN apt-get update \
    && apt-get install -y apt-cacher-ng vim git live-build texlive-lang-german texlive-latex-base texlive-latex-extra texlive-latex-recommended python-daemon python-gudev python-pam python-pyudev python-mock arandr docbook-to-man devscripts dpkg-dev reprepro sudo

RUN useradd -G sudo efalive && echo 'efalive:efalive' | chpasswd && chown efalive /home/efalive

RUN echo "efalive ALL=NOPASSWD: /etc/init.d/apt-cacher-ng start" >> /etc/sudoers

VOLUME ["/home/efalive/development"]

USER efalive

WORKDIR /home/efalive

CMD /bin/bash -c "sudo /etc/init.d/apt-cacher-ng start" && /bin/bash
