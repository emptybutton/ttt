FROM postgres:16.3-alpine3.19

ARG POSTGRES_REPLICA_PASSWORD
ARG POSTGRES_REPLICA_NAME

COPY \
    deploy/prod/postgres/common-postgres.conf \
    deploy/prod/postgres_replica/postgres.conf \
    deploy/prod/postgres_replica/start-server.sh \
    /mnt/

RUN echo "primary_conninfo = \
    'host=postgres_master \
    user=replica \
    password=${POSTGRES_REPLICA_PASSWORD} \
    application_name=${POSTGRES_REPLICA_NAME}'" \
    >> /mnt/postgres.conf
