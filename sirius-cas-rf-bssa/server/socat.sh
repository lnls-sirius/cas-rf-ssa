#!/bin/bash

socat -d -d pty,rawer,echo=0,crnl,link='/dev/rfBssaSerial' TCP4:${DEVICE_IP_ADDRESS}:${SOCAT_PORT}
