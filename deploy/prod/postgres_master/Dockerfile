FROM postgres:16.3-alpine3.19

COPY deploy/prod/postgres_master/init.sql /docker-entrypoint-initdb.d
COPY \
    deploy/prod/postgres/common-postgres.conf \
    deploy/prod/postgres_master/postgres.conf \
    deploy/prod/postgres_master/pg_hda.conf \
    /mnt/
