import io
import pycurl
import stem.control
import time

from utils import *


SOCKS_PORT = 9050
CONNECTION_TIMEOUT = 30  # timeout before we give up on a circuit

hops = 3

web_replicas = 10


def query(url):
    """
    Uses pycurl to fetch a site using the proxy on the SOCKS_PORT.
    """

    output = io.BytesIO()

    query = pycurl.Curl()
    query.setopt(pycurl.URL, url)
    query.setopt(pycurl.PROXY, 'localhost')
    query.setopt(pycurl.PROXYPORT, SOCKS_PORT)
    query.setopt(pycurl.PROXYTYPE, pycurl.PROXYTYPE_SOCKS5_HOSTNAME)
    query.setopt(pycurl.CONNECTTIMEOUT, CONNECTION_TIMEOUT)
    query.setopt(pycurl.WRITEFUNCTION, output.write)

    try:
        query.perform()
        return output.getvalue()
    except pycurl.error as exc:
        raise ValueError('Unable to reach %s (%s)' % (url, exc))


def scan(controller, path):
    """
    Fetch url through the given path of relays, providing back the time it took.
    """

    circuit_id = controller.new_circuit(path, await_build=True)

    def attach_stream(stream):
        if stream.status == 'NEW':
            controller.attach_stream(stream.id, circuit_id)

    controller.add_event_listener(attach_stream, stem.control.EventType.STREAM)

    try:
        controller.set_conf('__LeaveStreamsUnattached', '1')  # leave stream management to us
        start_time = time.time()

        target_service = f'private-tor-network-web-{sample(web_replicas) + 1}'
        print(f'target_service {target_service}')
        check_page = query(f'{target_service}:80')
        open(f'{data_dir}/stinger', 'w').write(f'{target_service}\n')
        print(check_page)

        return time.time() - start_time
    finally:
        controller.remove_event_listener(attach_stream)
        controller.reset_conf('__LeaveStreamsUnattached')


def trial():
    path = []

    for _ in range(hops - 1):
        path.append(sample_list(relay_fingerprints))

    path.append(sample_list(exit_fingerprints))

    try:
        time_taken = scan(controller, path)
        print('%s => %0.2f seconds' % (str(path), time_taken))
    except Exception as exc:
        print('%s => %s' % (str(path), exc))


if __name__ == '__main__':

    with stem.control.Controller.from_port(port=9051) as controller:
        controller.authenticate('password')

        exit_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses() if desc.nickname[:4] == 'EXIT']
        relay_fingerprints = [desc.fingerprint for desc in controller.get_network_statuses() if desc.nickname[:5] == 'RELAY']

        trial()
