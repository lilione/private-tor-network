import re

from enclave.python.utils import *


if __name__ == '__main__':

    w3 = get_web3()

    with open(f'{verify_path}', 'r') as f:
        evidence = eval(f.read())
        print(evidence)

    with open(f'{answer_path}', 'r') as f:
        answer = eval(f.read())
        print(answer)

    assert(evidence == answer)

    proof_blob = rlp.encode('OK')
    secret_key = open(secret_key_path, "rb").read()
    sig = sign_eth_data(w3, secret_key, proof_blob)
    print(f'proof_blob {proof_blob} proof_sig {sig}')
    open(os.path.join(output_dir, "proof_blob"), "wb").write(proof_blob)
    open(os.path.join(output_dir, "proof_sig"), "wb").write(sig)
