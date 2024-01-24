from tcp_client import *

if __name__ == '__main__':
    client = tcp_client(SERVER_HOST, SERVER_PORT)
    client.receive()
