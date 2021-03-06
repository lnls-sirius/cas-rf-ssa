# cas-rf
Sirius RF channel access related systems.

# SIRIUS-CAS-RF-RING

Channel Access server for the solid-state amplifiers of Sirius booster RF system.

Author: Eduardo Coelho<br>
Author: Claudio Carneiro

## Requirements
<ul>
    <li>
        Hardware requirements:<br>
        A FTDI-based USB/RS-485 converter with 500 kbps baud rate capability.<br>
        Tested with an interface powered by FTDI FT232RL and NVE IL3685 RS-485 transceiver.
    </li>
    <li>
        Software requirements:<br>
    </li>
</ul>

|Module|Value|
|:----:|:---:|
|ASYN|/opt/epics-R3.15.5/modules/asyn4-35|
|AUTOSAVE|/opt/epics-R3.15.5/modules/autosave-R5-9|
|CALC|/opt/epics-R3.15.5/modules/synApps/calc-R3-7-1|
|STREAM|/opt/epics-R3.15.5/modules/StreamDevice-2.8.8|
|EPICS_BASE|/opt/epics-R3.15.5/base|
 


## Installing
### procServ
Get the procServ-v2.8.0 tar file from `https://github.com/ralphlange/procServ/releases/download/v2.8.0/procServ-2.8.0.tar.gz`
```
wget https://github.com/ralphlange/procServ/releases/download/v2.8.0/procServ-2.8.0.tar.gz
tar -zxvf procServ-2.8.0.tar.gz
cd procServ-2.8.0
./configure --enable-access-from-anywhere
make install
cd ..
rm -rf procServ-2.8.0.tar.gz procServ-2.8.0
```

### User permission
This repository should be cloned at `/opt` <br>
Make sure that the user `iocuser` is created and is part of `dialout` and `ioc` groups <br>
Check the repository permisson
```
chown -R iocuser:ioc cas-rf-ssa
```

### Compiling
Booster
```
cd SSABoosterSup
make install-dependencies
cd ..
make
```
Storage Ring
```
cd SSAStorageRingSup
make install-dependencies
cd ..
make
```
Copy the correct service from `services`
```
cp services/<SERVICE> /etc/systemd/system
systemctl daemon-reload
systemctl enable <SERVICE>
systemctl start <SERVICE>
```
Error check
```
systemctl enable <SERVICE>
```
