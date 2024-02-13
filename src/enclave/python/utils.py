import json
import os
import random
import rlp
import socket
import time

from eth_account import Account
from eth_account.messages import encode_defunct
from web3.middleware import construct_sign_and_send_raw_middleware, geth_poa_middleware
from web3 import Web3, HTTPProvider

data_dir = "/private-tor-network/data/enclave"
input_dir = "/private-tor-network/data/input"
output_dir = "/private-tor-network/data/output"

subversion_service_path = f'{input_dir}/leak'
# cert_path = f'{input_dir}/tlscert.der'
verify_path = f'{input_dir}/verify'

backdoor_path = f'{output_dir}/backdoor'
enclave_address_path = f'{output_dir}/enclave_address'

stinger_path = f'{data_dir}/stinger'
answer_path = f'{data_dir}/answer'
secret_key_path = f'{data_dir}/secret_key'

HOST = socket.gethostbyname('ethnode')
PORT = 8545
endpoint = f"http://{HOST}:{PORT}"

BOUNTY_AMT = 150000000000000


def timestamp(str=''):
    with open('/private-tor-network/src/benchmark/latency.csv', 'a') as f:
        f.write(f"{str},{time.time()}\n")


def get_web3():
    w3 = Web3(HTTPProvider(endpoint))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    return w3


def setup_new_account(w3):
    new_account = w3.eth.account.create()
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(new_account))
    return new_account


def sample(range):
    return random.randint(0, range - 1)


def sample_list(arr):
    return arr[sample(len(arr))]


def sign_eth_data(w3, private_key, data):
    data = encode_defunct(primitive=data)
    res = w3.eth.account.sign_message(data, private_key)
    return res.signature


def get_account(w3, secret_key):
    account = Account.from_key(secret_key)
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
    return account
