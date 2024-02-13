#!/usr/bin/env bash

set -e
set -x

NUM_TRIALS=5

#rm -rf ./build
#truffle compile

make clean
make

if [[ "$SGX" == 1 ]]; then
    GRAMINE="gramine-sgx ./python"
elif [[ "$SGX" == -1 ]]; then
    GRAMINE="python3"
fi

data_dir=/private-tor-network/data/enclave
input_dir=/private-tor-network/data/input
output_dir=/private-tor-network/data/output

rm -rf $data_dir/*
rm -rf $input_dir/*
rm -rf $output_dir/*

for i in $(eval echo "{1..$NUM_TRIALS}")
do

  echo "$i" >> benchmark/latency.csv

  #$GRAMINE -m enclave.python.gen_signing_key
  #
  #if [[ "$SGX" == 1 ]]; then
  ##    $GRAMINE -m enclave.python.sgx_report &> OUTPUT
  ##    grep -q "Generated SGX report" OUTPUT && echo "[ Success SGX report ]"
  #    $GRAMINE -m enclave.python.sgx_quote &>> OUTPUT
  #    grep -q "Extracted SGX quote" OUTPUT && echo "[ Success SGX quote ]"
  #    cat OUTPUT
  #    gramine-sgx-ias-request report --api-key $RA_TLS_EPID_API_KEY --quote-path "${output_dir}/quote" --report-path ias.report --sig-path ias.sig -c ias.cert -v
  #fi
  #
  #python3 -m interact_contract setup_bounty_contract
  #python3 -m interact_contract submit_enclave

  $GRAMINE -m enclave.python.create_stinger
  $GRAMINE -m enclave.python.leave_backdoor

  python3 -m make_evidence

  $GRAMINE -m enclave.python.verify_evidence

done
