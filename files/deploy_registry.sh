#!/usr/bin/env bash

FTP_USER="${1}"
FTP_SECRET="${2}"
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

if [ -z "${FTP_USER}" ]; then
    echo "First parameter FTP_USER is missing!"
    exit 1
fi

if [ -z "${FTP_SECRET}" ]; then
    echo "Second parameter FTP_SECRET is missing!"
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

lftp -e "mirror -n debian repository && bye" --user "${FTP_USER}" --password "${FTP_SECRET}" ftp://wp1152936.server-he.de

cd repository
reprepro remove $DISTRIBUTION $SOFTWARE
reprepro -Vb . includedeb $DISTRIBUTION ../$PACKAGE
cd ..

lftp -e "mirror -R -n repository debian && bye" -u "${FTP_USER}","${FTP_SECRET}" ftp://wp1152936.server-he.de

