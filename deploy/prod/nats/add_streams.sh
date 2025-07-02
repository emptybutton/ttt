#!/bin/bash

nats -s nats://nats:4222 stream add --config /mnt/streams/player.json
