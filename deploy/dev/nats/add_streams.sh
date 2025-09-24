#!/bin/bash

for stream_config_file in `ls -lx /mnt/streams`; do
    nats -s nats://nats:4222 stream add --config /mnt/streams/$stream_config_file
done
