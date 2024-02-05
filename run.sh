#!/usr/bin/env bash

if [[ "$SGX" == 1 ]]; then
    docker compose up -d
elif [[ "$SGX" == -1 ]]; then
    docker compose -f docker-compose-no-sgx.yml up -d
fi
