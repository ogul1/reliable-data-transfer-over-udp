import socket


class tcp_server:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

    def send(self, data):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind((self.server_host, self.server_port))
            s.listen()
            conn, addr = s.accept()
            with conn:
                for file in data:
                    conn.sendall('{:08d}'.format(len(file)).encode())
                    conn.sendall(file)
