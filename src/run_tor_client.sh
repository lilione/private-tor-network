cd /private-tor-network/src
make clean || true
make

cd /private-tor-network
make clean || true
make

rm -rf /private-tor-network/data/enclave/*

gramine-sgx tor
#tor -f /etc/tor/torrc
