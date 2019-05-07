import sys
sys.path.append("..")

import socket
import signal
from logConfig import logger
import threading

class Handler(threading.Thread):
    def __init__(self, call, arg):
        self.fun = call
        self.arg = arg
        self.flag = True
        threading.Thread.__init__(self)

    def run(self):
        self.fun(self.arg)
    
    def stop(self):
        self.flag = False

class CrawlServer(threading.Thread):
    def __init__(self, callback, host = "127.0.0.1", port = 8000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.callback = callback
        self.flag = True

        try:
            self.sock.bind((host, port))
        except Exception as identifier:
            logger.error("socket bind error %s" % identifier)
            sys.exit()

        self.sock.listen(10)
        threading.Thread.__init__(self)

    def startListening(self):
        # 向客户端保持连接
        while True and self.flag:
            conn, addr = self.sock.accept()
            logger.info("%s: %s" % (conn, addr))

            # 开新线程来进行通信
            handler = Handler(self.clientThread, conn)
            handler.start()

    def clientThread(self, conn):
        datas = conn.recv(1024)
        logger.info("From Client Datas: %s" % datas)
        reply = self.callback(datas)
        conn.sendall(reply)
        conn.close()

    def run(self):
        self.startListening()

    def stop(self):
        self.flag = False
        self.sock.close()

def msg_received(data):
    return "ACK".encode()

def exit_signal_handler(signal, frame):
    pass

if __name__ == "__main__":
    server = CrawlServer(msg_received)
    server.start()
    signal.signal(signal.SIGINT, exit_signal_handler)
    signal.pause()
    server.stop()
    sys.exit()