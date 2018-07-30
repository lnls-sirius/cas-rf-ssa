#!/bin/sh

docker run -d \
    -p 4161:4161 \
    -e SOCAT_PORT=4161 \
    -e DEVICE_IP_ADDRESS=10.0.28.69 \
    -e RF_RING_SERIAL_PORT="/dev/rfRingSerial" \
    -e PYTHONPATH=/root/cas-rf/sirius-cas-rf-ring/server \
    --name rf-ring lnlscon/rf-ring:latest