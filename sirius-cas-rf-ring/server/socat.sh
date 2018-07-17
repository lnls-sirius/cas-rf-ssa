#!/bin/bash

socat -d -d pty,rawer,echo=0,crnl,link=${RF_RING_SERIAL_PORT} TCP4:${DEVICE_IP_ADDRESS}:${SOCAT_PORT}
