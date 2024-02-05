#!/usr/bin/env bash

set -e
set -x

if [[ "$SGX" == 1 ]]; then
    GRAMINE="gramine-sgx ./python"
elif [[ "$SGX" == -1 ]]; then
    GRAMINE="python3"
fi

data_dir=/private-tor-network/data/enclave
input_dir=/private-tor-network/data/input
output_dir=/private-tor-network/data/output

rm -rf $data_dir || true
rm -rf $input_dir || true
rm -rf $output_dir || true

mkdir -p $data_dir
mkdir -p $input_dir
mkdir -p $output_dir


$GRAMINE -m enclave.python.gen_signing_key

$GRAMINE -m enclave.python.create_stinger
$GRAMINE -m enclave.python.leave_backdoor

python3 -m make_evidence

$GRAMINE -m enclave.python.verify_evidence



