#!/bin/bash

if [ ! -f /var/lib/postgresql/data/standby.signal ]; then
  echo 'Copying data from master...';
  pg_basebackup -h postgres_master -U replica -D /var/lib/postgresql/data -P -R -X stream;
fi;

echo 'Starting PostgreSQL replica...';
exec docker-entrypoint.sh postgres -c config_file=/mnt/postgres.conf;
