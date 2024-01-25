import os
import random
import socket

from web3.middleware import construct_sign_and_send_raw_middleware
from web3 import Web3, HTTPProvider

if int(os.environ.get("INSIDE_SGX", 0)) == 1:
    data_dir = "/data"
    input_dir = "/input"
    output_dir = "/output"
else:
    data_dir = '/private-tor-network/src/enclave_data'
    input_dir = "/private-tor-network/src/input_data"
    output_dir = "/private-tor-network/src/output_data"

secret_key_path = f'{data_dir}/secret_key'

HOST = socket.gethostbyname('ethnode')
PORT = 8545
endpoint = f"http://{HOST}:{PORT}"


def get_web3():
    w3 = Web3(HTTPProvider(endpoint))
    return w3


def setup_new_account(w3):
    new_account = w3.eth.account.create()
    w3.middleware_onion.add(construct_sign_and_send_raw_middleware(new_account))
    return new_account


def sample(range):
    return random.randint(0, range - 1)


def sample_list(arr):
    return arr[sample(len(arr))]
