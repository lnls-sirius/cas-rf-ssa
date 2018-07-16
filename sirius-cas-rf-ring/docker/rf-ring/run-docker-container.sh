#!/bin/sh

docker run -d \
    -p 4161:4161 \
    --name rf-ring lnlscon/rf-ring:latest
