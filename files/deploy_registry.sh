#!/usr/bin/env bash

SSH_USER="${1}"
SSH_HOST="${2}"
DISTRIBUTION="${3}"
SOFTWARE="${4}"
VERSION="${5}"
CREATE_RELEASE=true

set -e

if [ -f release_info.sh ]; then
    source release_info.sh
fi

if [ "${CREATE_RELEASE}" != "true" ]; then
    echo "Skip deployment since there is no new release"
    exit 0
fi

if [ -z "${SSH_USER}" ]; then
    echo "First parameter SSH_USER is missing!"
    exit 1
fi

if [ -z "${SSH_HOST}" ]; then
    echo "Second parameter SSH_HOST is missing!"
    exit 1
fi

if [ -z "${DISTRIBUTION}" ]; then
    echo "Third parameter DISTRIBUTION is missing!"
    exit 1
fi

if [ -z "${SOFTWARE}" ]; then
    echo "Fourth parameter SOFTWARE is missing!"
    exit 1
fi

if [ -z "${VERSION}" ]; then
    echo "Fifth parameter VERSION is missing!"
    exit 1
fi

PACKAGE="${SOFTWARE}_${VERSION}_all.deb"

rsync -rltv --delete -e 'ssh -o StrictHostKeyChecking=no' ${SSH_USER}@${SSH_HOST}:efalive/debian/ repository/

cd repository
reprepro remove $DISTRIBUTION $SOFTWARE
reprepro -Vb . includedeb $DISTRIBUTION ../$PACKAGE
cd ..

rsync -rltv --delete -e 'ssh -o StrictHostKeyChecking=no' repository/ ${SSH_USER}@${SSH_HOST}:efalive/debian/

