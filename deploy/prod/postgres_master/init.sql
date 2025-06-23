\set replica_password `echo $POSTGRES_REPLICA_PASSWORD`

CREATE ROLE replica WITH LOGIN PASSWORD ':replica_password' REPLICATION;
