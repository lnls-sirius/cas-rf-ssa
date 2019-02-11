
PREFIX ?= /usr/local

SOCAT_SERVICE_NAME = rf-ring-socat
SOCAT_SRC_SERVICE_FILE = ${SOCAT_SERVICE_NAME}.service

SERVICE_NAME = rf-ring
SRC_SERVICE_FILE = ${SERVICE_NAME}.service

SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall

all: install

install:
	pip3 install -r requirements.txt

	/bin/cp -rf ${SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SERVICE_NAME}
	systemctl start ${SERVICE_NAME}
	systemctl enable ${SERVICE_NAME}
	@echo "\n$@ finished!"

uninstall:
	@echo "Executing $@..."
	systemctl stop ${SERVICE_NAME}
	systemctl disable ${SERVICE_NAME}
	/bin/rm -f ${SERVICE_FILE_DEST}/${SRC_SERVICE_FILE}

	systemctl daemon-reload

