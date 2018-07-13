#!/bin/bash

# Bind using TCP
socat -d -d TCP-LISTEN:${SOCAT_PORT},reuseaddr FILE:/dev/ttyUSB0,b500000,rawer,crnl
