cd /private-tor-network/src/enclave/python
make clean
make

cd /private-tor-network
make clean || true
make

gramine-sgx tor
