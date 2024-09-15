#!/bin/bash -xe

# Initialise
version=${CI_PIPELINE_ID:-$(date -u +%Y%m%d%H%M%S)}
echo -en '# -*- mode: python; coding: utf-8; -*-\n__version__ = '\'"$version"\''\n' > _version.py
CA_VERSION=$version
export CA_VERSION
ca init '>=8'

# Download
ca docker_pull baseimages/rcdcdashrep_ubuntu_2004_amd64
MYSQL_IMAGE=bitnami/mysql:8.0.36
ca docker_pull $MYSQL_IMAGE
KAFKA_IMAGE=bitnami/kafka:3.7.0
ca docker_pull $KAFKA_IMAGE


chmod +x ./run-with-mysql
chmod +x ./run-with-kafka
chmod +x ./make.sh
chmod +x ./setup.py

# Build
ca build --buildenv baseimages/rcdcdashrep_ubuntu_2004_amd64 --cmd "MYSQL_IMAGE=$MYSQL_IMAGE KAFKA_IMAGE=$KAFKA_IMAGE ./run-with-mysql ./run-with-kafka ./make.sh"

# List the contents of the dist directory to verify the wheel file
ls -l dist/

# Publish
ca publish dist/tangedcofmsrep-"${CA_VERSION}"-py3-none-any.whl,metadata

# Trigger
# (no builds to trigger)

# Install the generated wheel
#virtualenv -p python3 --system-site-packages ve
# shellcheck disable=SC2102
#./ve/bin/pip install dist/lastgasp_ynr_report-"${CA_VERSION}"-py3-none-any.whl[test] --only-binary=cryptography,cffi
