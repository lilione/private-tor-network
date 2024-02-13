import re

from enclave.python.utils import *


if __name__ == '__main__':
    answer = dict()
    backdoor = ''

    timestamp('leave_backdoor')

    with open(f'{stinger_path}', 'r') as f:
        for line in f.readlines():
            elements = re.split(r'\s+|:', line)
            if elements[2][:7] == 'private':
                answer[elements[1]] = elements[2]
                backdoor += f'{elements[1]}\n'

    with open(f'{backdoor_path}', 'w') as f:
        f.write(backdoor)

    with open(f'{answer_path}', 'w') as f:
        f.write(str(answer))

    timestamp('leave_backdoor')
