#!/usr/bin/env bash

if [[ "$SGX" == 1 ]]; then
    docker compose down -v --remove-orphans
elif [[ "$SGX" == -1 ]]; then
    docker compose -f docker-compose-no-sgx.yml down -v --remove-orphans
fi

sudo rm -rf tor
sudo rm -rf data/*
