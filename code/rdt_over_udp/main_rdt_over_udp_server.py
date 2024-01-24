from rdt_over_udp_server import *
from constants import *


# reads all the files in chunks and creates a python generator object
def chunk_generator(chunk_size=DATA_PAYLOAD_SIZE):
    # 0 -> large0, 2 -> large1, 4 -> large2, ...
    # 1 -> small0, 3 -> small1, 5 -> small2, ...
    # if odd then we know it's a small file
    # if even then we know it's a large file
    # always do integer division by 2 to find the index (implemented in the client side)
    for i in range(NUMBER_OF_FILES // 2):
        with open("../../root/objects/large-" + str(i) + ".obj", "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk

        # indicates the end of a file
        yield b''

        with open("../../root/objects/small-" + str(i) + ".obj", "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk:
                    break
                yield chunk
        yield b''


if __name__ == '__main__':
    # starts the rdt over udp server using the corresponding host and port numbers
    server = rdt_over_udp_server(SERVER_HOST, SERVER_PORT, CLIENT_HOST, CLIENT_PORT, chunk_generator())
    server.send()
