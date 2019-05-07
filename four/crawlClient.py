import sys
sys.path.append("..")

import socket
from logConfig import logger

class CrawlClient:
    def __init__(self, serverIp = "127.0.0.1", serverPort = 8000):
        self.serverIp = serverIp
        self.serverPort = serverPort
        self.families = self.get_constants("AF_")
        self.types = self.get_constants("SOCK_")
        self.protocols = self.get_constants("IPPROTO_")

    def get_constants(self, prefix):
        return dict(
            (getattr(socket, n), n)
            for n in dir(socket) if n.startswith(prefix)
        )

    def send(self, message):
        try:
            self.sock = socket.create_connection((self.serverIp, self.serverPort))
            self.sock.sendall(message)

            datas = self.sock.recv(1024)
            logger.info("From Server Datas: %s" % datas)
            return datas
        except Exception as identifier:
            logger.error("Client error %s" % identifier)
        finally:
            self.sock.close()

if __name__ == "__main__":
    client = CrawlClient()
    client.send("what the fuck".encode())