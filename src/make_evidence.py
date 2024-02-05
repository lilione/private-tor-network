import re

from enclave.python.utils import *


if __name__ == '__main__':
    map = dict()

    with open(f'{subversion_service_path}', 'r') as f:
        for line in f.readlines():
            elements = re.split(r'\s+|:', line)
            map[elements[1]] = elements[2][1:-1]

    with open(f'{verify_path}', 'w') as f:
        f.write(str(map))
