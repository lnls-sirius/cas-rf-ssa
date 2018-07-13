
PREFIX ?= /usr/local

SOCAT_SERVICE_NAME = rf-ring-socat
SOCAT_SRC_SERVICE_FILE = ${SOCAT_SERVICE_NAME}.service

SERVICE_NAME = rf-ring
SRC_SERVICE_FILE = ${SERVICE_NAME}.service

SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install-socat install uninstall

all: install
 
install:
	@echo Installing Python3 and pip3!
	apt-get install python3
	apt-get install python3-pip
	pip3 install -r requirements.txt

	@echo "Executing $@...\n"
	@echo "Installing socat service!"
	/bin/cp -rf ${SOCAT_SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SOCAT_SERVICE_NAME}
	systemctl start ${SOCAT_SERVICE_NAME}
	systemctl enable ${SOCAT_SERVICE_NAME}

	@sleep 1

	@echo "\n"
	@echo "Installing python ioc service!"
	/bin/cp -rf ${SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SERVICE_NAME}
	systemctl start ${SERVICE_NAME}
	systemctl enable ${SERVICE_NAME}
	@sleep 1

	@echo "\n$@ finished!"

uninstall: 
	@echo "Executing $@..."

	systemctl stop ${SERVICE_NAME}
	systemctl disable ${SERVICE_NAME}
	/bin/rm -f ${SERVICE_FILE_DEST}/${SRC_SERVICE_FILE}
	
	@sleep 1
	
	systemctl stop ${SOCAT_SERVICE_NAME}
	systemctl disable ${SOCAT_SERVICE_NAME}
	/bin/rm -f ${SERVICE_FILE_DEST}/${SOCAT_SRC_SERVICE_FILE}

	systemctl daemon-reload
	
