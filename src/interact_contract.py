import base64
import re
import sys

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from enclave.python.utils import *
from eth_abi import encode

SOLIDITY_PATH = "../build/contracts/Honeypot.json"

cert_ending = '-----END CERTIFICATE-----\n'


def setup_bounty_contract(w3):
    bounty_admin = get_account(w3, os.environ.get("BOUNTY_CONTRACT_ADMIN_PK", "0xc8ae83e52a1593ac42fc6868dbdbf9af7a09678b4f3331d191962e582133b78d"))
    contract_address, contract = deploy_contract(w3, bounty_admin.address)
    with open("contract_address", "w") as f:
        f.write(contract_address)


def deploy_contract(w3, admin_addr):
    abi, bytecode = parse_contract(SOLIDITY_PATH)
    contract = w3.eth.contract(abi=abi, bytecode=bytecode)
    tx_hash = contract.constructor().transact({"from": admin_addr, "value": BOUNTY_AMT})
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
    contract_address = receipt['contractAddress']
    contract = w3.eth.contract(address=contract_address, abi=abi)
    print(f'Deployed Honeypot contract to: {contract_address} with hash  {tx_hash.hex()}')
    return contract_address, contract


def parse_contract(contract_path):
    contract = json.load(open(contract_path))
    return contract['abi'], contract['bytecode']


def submit_enclave(w3):
    contract = get_contract(w3)
    informant_account = get_account(w3, os.environ.get("INFORMANT_PK", "0x3b7cd6efb048079f7e5209c05d74369600df0d15fc177be631b3b4f9a84f8abc"))
    # print(f'informant_account {informant_account.address} balance: {w3.eth.get_balance(informant_account.address)}')
    enclave_address = open(enclave_address_path).read()
    if int(os.environ.get("SGX", 1)) == 1:
        report = open("ias.report").read()
        report_json = json.loads(report)
        quote = base64.b64decode(report_json["isvEnclaveQuoteBody"])
        with open("ias.sig") as f:
            ias_sig_b64 = f.read()
        ias_sig = base64.b64decode(ias_sig_b64)
        assert enclave_address == Web3.toChecksumAddress(quote[368:388].hex())
    else:
        report = "ias report"
        ias_sig = b"ias sig"
    # print(f'!!! enclave_address {enclave_address}')
    # print(f"!!! ias report {bytes(report, 'utf-8').hex()}")
    report_bytes = encode(
        ['bytes', 'bytes', 'bytes', 'bytes', 'bytes', 'bytes', 'bytes', 'bytes'],
        [
            bytes(report_json['id'], 'utf-8'),
            bytes(report_json['timestamp'], 'utf-8'),
            bytes(str(report_json['version']), 'utf-8'),
            bytes(report_json['advisoryURL'], 'utf-8'),
            bytes(re.sub("'", '"',json.dumps(str(report_json['advisoryIDs'])).replace(" ", "")), 'utf-8')[1:-1],
            bytes(report_json['isvEnclaveQuoteStatus'], 'utf-8'),
            bytes(report_json['platformInfoBlob'], 'utf-8'),
            base64.b64decode(report_json['isvEnclaveQuoteBody'])
        ]
    )
    # print("!!! ias sig", base64.b64decode(ias_sig_b64).hex())
    certs = re.split(cert_ending, open("ias.cert").read())
    child_cert_str = certs[0] + cert_ending
    cert = x509.load_pem_x509_certificate(child_cert_str.encode('ascii'))
    cert_der = cert.public_bytes(serialization.Encoding.DER)
    # print("!!! payload", enclave_address)

    quote = base64.b64decode(report_json["isvEnclaveQuoteBody"])
    mrenclave = quote[112:144]
    mrsigner = quote[176:208]
    gas = send_tx(w3, contract.functions.submitEnclave(report_bytes, ias_sig, cert_der, mrenclave, mrsigner), informant_account.address)
    # with open('"/Sting-Flashbots/searcher/benchmark/benchmark_gas.csv', 'a') as f:
    #     f.write(f"submitEnclave,{gas}\n")


def get_contract(w3):
    abis, bins = parse_contract(SOLIDITY_PATH)
    contract_address = open("contract_address").read()
    print("contract_address", contract_address)
    return w3.eth.contract(abi=abis, bytecode=bins, address=contract_address)


def send_tx(w3, foo, user_addr, value=0):
    print(f"send_tx from address: {user_addr} {foo}")
    try:
        gas_estimate = foo.estimateGas()  # for some reason this fails sometimes when it shouldn't
    except Exception as e:
        print(f"estimate gas error {e}")
        gas_estimate = 0
        pass

    if gas_estimate < 10000000:
        tx_hash = foo.transact({"from": user_addr, "value": value})
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"transaction receipt mined: {receipt}")
        return receipt.gasUsed
    else:
        print(f"send_tx error Gas cost exceeds 10000000 < {gas_estimate}")
        exit(1)


if __name__ == '__main__':
    print(f'========================================================================= {sys.argv[1]}')

    w3 = get_web3()
    globals()[sys.argv[1]](w3)

    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
