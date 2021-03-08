#!/usr/bin/env bash

pushd create_release
poetry install
poetry run pytest
poetry build -f wheel
popd

cp create_release/dist/create_release-0.1.0-py3-none-any.whl files/

