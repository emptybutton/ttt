#!/bin/bash

prefix=./deploy/prod

main=${prefix}/docker-compose.yaml
postgres_bootstrap=${prefix}/docker-compose.postgres-bootstrap.yaml

docker compose -f ${main} build
docker compose -f ${main} rm -sf

docker compose -f ${postgres_bootstrap} up -d --wait
docker compose -f ${postgres_bootstrap} rm -sf

docker compose -f ${main} run ttt alembic upgrade head
docker compose -f ${main} up -d
