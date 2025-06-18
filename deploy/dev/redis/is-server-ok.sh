#!/bin/bash

echo PING | redis-cli | grep -qF PONG
