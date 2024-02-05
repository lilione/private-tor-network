docker compose -f docker-compose-no-sgx.yml build client
docker compose -f docker-compose-no-sgx.yml up -d --no-deps client
docker compose -f docker-compose-no-sgx.yml logs -f client
docker compose -f docker-compose-no-sgx.yml exec client bash