#!/bin/bash
set -x
cp -p -f rf-ssa-booster.service /etc/systemd/system

pip3 install -r requirements.txt

systemctl daemon-reload
systemctl enable rf-ssa-booster.service
systemctl start  rf-ssa-booster.service
