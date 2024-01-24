import socket
from constants import *


class tcp_client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

    def receive(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.connect((self.server_host, self.server_port))
            for i in range(NUMBER_OF_FILES):
                file_size = int(s.recv(8))
                buffer = b''
                while len(buffer) < file_size:
                    buffer += s.recv(min(file_size - len(buffer), DATA_PAYLOAD_SIZE))
                if not buffer:
                    break
                file_name = ("large-" if i % 2 == 0 else "small-") + str(i // 2) + ".obj"
                with open(file_name, "wb") as f:
                    f.write(buffer)
