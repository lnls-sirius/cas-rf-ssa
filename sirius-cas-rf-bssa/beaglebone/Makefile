PREFIX ?= /usr/local

SERVICE_NAME = rf-bssa-socat
SRC_SERVICE_FILE = ${SERVICE_NAME}.service
SERVICE_FILE_DEST = /etc/systemd/system

.PHONY: all install uninstall

all:

install:
	@echo "\n"
	@echo "Installing socat"
	apt-get install socat

	@echo "Executing $@...\n"
	@echo "Installing socat service!"
	cp --preserve=mode ${SRC_SERVICE_FILE} ${SERVICE_FILE_DEST}
	systemctl daemon-reload
	systemctl stop ${SERVICE_NAME}
	systemctl start ${SERVICE_NAME}
	systemctl enable ${SERVICE_NAME}

uninstall:
	@echo "Executing $@..."
	systemctl stop ${SERVICE_NAME}
	systemctl disable ${SERVICE_NAME}
	rm -f ${SERVICE_FILE_DEST}/${SRC_SERVICE_FILE}
	systemctl daemon-reload
