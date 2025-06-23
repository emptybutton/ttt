\set replica_password `echo $POSTGRES_MASTER_REPLICA_PASSWORD`
\set ttt_password `echo $POSTGRES_MASTER_TTT_PASSWORD`

CREATE ROLE replica WITH LOGIN PASSWORD ':replica_password' REPLICATION;
CREATE ROLE ttt WITH LOGIN PASSWORD ':ttt_password';

CREATE DATABASE ttt;
