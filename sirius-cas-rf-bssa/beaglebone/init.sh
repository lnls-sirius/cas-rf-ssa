#!/bin/bash

# Bind using TCP
socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr,range=${SERVER_IP_ADDR}:${SERVER_MASK} FILE:/dev/ttyUSB0,b500000,rawer,crnl
