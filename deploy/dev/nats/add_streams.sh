#!/bin/bash

for stream_config_file in `ls -lx /mnt/streams`; do
    nats stream add --config /mnt/streams/$stream_config_file
done
