#!/usr/bin/python3
import random
import socket
import os
import logging
import argparse
import typing


class Hardware:
    def _message(self, LENGTH: int) -> str:

        """Byte 7  = On/Off"""
        ON = "1"
        SEPARATOR = ";"

        RES = "1S01000"
        RES += ON
        RES += SEPARATOR

        b_n = 1
        b_i = 1
        for _ in range(int((LENGTH - 18) / 9)):
            BAR_NUM = "{}".format(b_n)
            BAR_ITEM = "{0:02d}".format(b_i)
            if b_i == 38:
                b_i = 1
                b_n += 1
            else:
                b_i += 1
            ADC = "{0:04d}".format(random.randint(0, 4096))
            RES += "1" + BAR_NUM + BAR_ITEM + ADC + SEPARATOR
        RES += "####FIM!;"

        return RES

    def get(self, command: str) -> str:
        if command == "TORRE1":
            response = self._message(2790)
        elif command in ["RACK{}".format(i) for i in range(1, 5)]:
            response = self._message(738)
        return response + "\r\n"


class Comm:
    def __init__(self, socket_path="./socket"):
        self.socket_path = socket_path
        self.connection: typing.Optional[socket.socket] = None
        self.welcome_socket: typing.Optional[socket.socket] = None
        self.hardware: Hardware = Hardware()

    def _clear(self):
        if os.path.exists(self.socket_path):
            os.unlink(self.socket_path)

        if self.welcome_socket != None:
            logger.warning("welcome socket already instantiated")

    def _close(self):
        self.welcome_socket.close()
        self.welcome_socket = None
        os.remove(self.socket_path)

    def _handle(self, connection: socket.socket):
        while True:
            with connection:
                command = connection.recv(1024).decode("utf-8")

                if not command:
                    raise RuntimeWarning("Empty command")

                response = self.hardware.get(command=command)

                connection.sendall(response.encode("utf-8"))
                logger.info("{} {}".format(command, response))

    def serve(self):
        try:
            self._clear()
            self.welcome_socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.welcome_socket.bind(self.socket_path)

            self.welcome_socket.listen(1)

            while True:
                connection, addr = self.welcome_socket.accept()
                logger.info("Client {} connected at {}".format(connection, addr))
                self._handle(connection=connection)
        except RuntimeWarning as e:
            logger.warning(f"Client disconnected, {e}")
        except Exception:
            logger.exception("Failed to init server")

        finally:
            self._close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Dummy RF SSA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.debug else logging.INFO,
        format="%(asctime)-15s [%(levelname)s] %(message)s",
        datefmt="%d/%m/%Y %H:%M:%S",
    )
    logger = logging.getLogger()

    comm = Comm()
    comm.serve()
