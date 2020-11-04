#!/usr/bin/env bash

PACKAGE="${1}"
SOFTWARE="${2}"
VERSION="${3}"
FTP_USER="${4}"
FTP_SECRET="${5}"

set -e

if [ -z "${PACKAGE}" ]; then
    echo "First parameter PACKAGE is missing!"
    exit 1
fi

if [ -z "${SOFTWARE}" ]; then
    echo "Second parameter SOFTWARE is missing!"
    exit 1
fi

if [ -z "${VERSION}" ]; then
    echo "Third parameter VERSION is missing!"
    exit 1
fi

if [ -z "${FTP_USER}" ]; then
    echo "Fourth parameter FTP_USER is missing!"
    exit 1
fi

if [ -z "${FTP_SECRET}" ]; then
    echo "Fifth parameter FTP_SECRET is missing!"
    exit 1
fi

lftp -e "mirror --verbose=2 -n debian repository && bye" --user "${FTP_USER}" --password "${FTP_SECRET}" ftp://wp1152936.server-he.de

cd repository
reprepro remove $VERSION $SOFTWARE
reprepro -Vb . includedeb $VERSION ../$PACKAGE
cd ..

lftp -e "mirror -R --verbose=2 -n repository debian && bye" -u "${FTP_USER}","${FTP_SECRET}" ftp://wp1152936.server-he.de

