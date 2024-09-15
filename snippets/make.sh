#!/bin/bash -xe

# configure proxy (if present) -- should succeed/fail quickly
if (exec 9</dev/tcp/squid/3128); then
    export http_proxy='http://squid:3128'
    export https_proxy='http://squid:3128'
    export no_proxy='localhost,127.0.0.1,::1,*.cyco.io'
fi

# build package
./setup.py bdist_wheel

# create virtualenv
virtualenv -p python3 --system-site-packages ve
echo CA_VERSION="${CA_VERSION}"
# install package, install dependencies, and test dependencies
# shellcheck disable=SC2102
./ve/bin/pip install dist/tangedcofmsrep-"${CA_VERSION}"-py3-none-any.whl[test] --only-binary=cryptography,cffi

# create config file
sed -e "s/\$MYSQL_HOST/$MYSQL_HOST/g; s/\$MYSQL_PORT/$MYSQL_PORT/g; s/\$MYSQL_USER/$MYSQL_USER/g; s/\$MYSQL_PASSWORD/$MYSQL_PASSWORD/g; s/\$MYSQL_DATABASE/$MYSQL_DATABASE/g; s/\$KAFKA_HOST/$KAFKA_HOST/g; s/\$KAFKA_PORT/$KAFKA_PORT/g; s/\$KAFKA_USER/$KAFKA_USER/g; s/\$KAFKA_PASSWORD/$KAFKA_PASSWORD/g; s@\$KAFKA_CA_CRT@$KAFKA_CA_CRT@g; s/\$KAFKA_BOOTSTRAP_SERVERS/$KAFKA_BOOTSTRAP_SERVERS/g;" config.conf.in >reports_path.conf

# run pytest, generate coverage report
./ve/bin/pytest --cov-branch --cov-report=term --cov-report=html --doctest-modules --cov=src -vvv test/

# archive coverage report for publishing to gitlab
zip -9r htmlcov-"${CA_VERSION}".zip htmlcov/
