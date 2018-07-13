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
        Python 2, EPICS Base and pcaspy.<br>
        Tested with Python 2.7.12, EPICS Base 3.15.5 and pcaspy 0.7.1,  socat 1.7.3.1-2+deb9u1 armhf and socat 1.7.3.2-2ubuntu2 amd64.
    </li>
</ul>

<p>
A single board computer (Beaglebone Black) is used to acquire the values from the RF system and serve it on the network via TCP. <br>"Socat is a command line based utility that establishes two bidirectional byte streams and transfers data between them."
</p>

<p>
On the server side Socat is also used to bind the communication to a virtual serial port. All processing is done on the server side.
<br>"PCASpy provides not only the low level python binding to EPICS Portable Channel Access Server but also the necessary high level abstraction to ease the server tool programming."
</p>

## Installation
<p>
The installation process is meant to be as simple as possible.<br>
It's important to set the correct values for the following enviroment variables inside the .services files:

`Environment=DEVICE_IP_ADDRESS=(beaglebone ipv4 addr)`<br>
`into`<br>`sirius-cas-rf-ring/server/rf-ring-socat.service`<br>
 
`Environment=SOCAT_PORT=(this port must be the same on the client and the server)`<br>
`into`<br>`sirius-cas-rf-ring/server/rf-ring-socat.service and sirius-cas-rf-ring/beaglebone/rf-ring-socat.service`<br>

When everything is set:<br>
`make install or make uninstall`
</p>

## OPI
<p>
Control System Studio is an Eclipse-based collection of tools to monitor and operate large scale control systems, such as the ones in the accelerator community. It's a product of the collaboration between different laboratories and universities.<br>

Set the channel access to the correct ip and configure the following macros:
<ul>
    <li>$(PREFIX) The first piece in the pv naming system</li>
    <li>$(TITLE) Just the opi title, no real purpose but looks.</li>
</ul>
</p>

To persist the values of the offset/alarm pvs, hit the save button.


# Sirius Cas Rf Booster