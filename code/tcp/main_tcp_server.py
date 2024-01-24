from tcp_server import *
from constants import *

if __name__ == '__main__':
    server = tcp_server(SERVER_HOST, SERVER_PORT)
    data = []
    for i in range(NUMBER_OF_FILES // 2):
        with open("../../root/objects/large-" + str(i) + ".obj", "rb") as f:
            data.append(f.read())
        with open("../../root/objects/small-" + str(i) + ".obj", "rb") as f:
            data.append(f.read())
    server.send(data)
