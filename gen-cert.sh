#!/bin/bash

# if there are certificates, skip this script
# if mkcert commands is not installed, skip this script

if [ -d "./certificates" ]; then
    echo "Certificates already exist"
    exit 1
elif ! command -v mkcert &> /dev/null; then
    echo "Make sure to install mkcert. https://github.com/FiloSottile/mkcert"
    exit 1
fi

mkdir certificates
cd certificates
mkcert localhost
mkcert server1
mkcert server2
mkcert server3
mkcert load_balancer
