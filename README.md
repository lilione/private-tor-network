### Prepare modified tor library
```bash
git checkout lilione
cd src
git clone https://github.com/lilione/tor.git
cd tor
git checkout sting
```

### Start Service
At root directory
```bash
docker compose up -d
```
The service is ready if run ```python util/get_consensus.py``` (on the host machine) output list of running Tor nodes.

### Craete stinger
```bash
docker compose exec client bash
gramine-sgx python -m create_stinger
```

### Subversion Service
See exit nodes' log, search for "!!!", you'll see the target service being accessed.

### TODO
The only modification I made in Tor codebase is in ```/src/tor/src/or/connection_edge.c```.
You can search for "!!!".
I'd like to print target services being accessed into a file, which was commented (line 813-815 in connection_edge.c).
But that code doesn't work as expected.

### Shut Down Service
```
docker compose down -v --remove-orphans
sudo rm -rf tor
```

If the client image is rebuilt, you don't need to restart the whole service. Just run ```docker compose up -d --no-deps client```.
You have to restart the whole service if tor node's (node.Dockerfile) is updated.