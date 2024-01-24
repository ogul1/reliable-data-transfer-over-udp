from rdt_over_udp_client import *


if __name__ == '__main__':
    # starts the client using the client host and port number
    client = rdt_over_udp_client(CLIENT_HOST, CLIENT_PORT)
    # 0 -> large0, 2 -> large1, 4 -> large2, ...
    # 1 -> small0, 3 -> small1, 5 -> small2, ...
    # if odd then we know it's a small file
    # if even then we know it's a large file
    # always do integer division by 2 to find the index
    file_data = [bytes() for i in range(NUMBER_OF_FILES)]

    # add the chunks to the data entry that they belong to using the stream_id identifier
    for stream_id, chunk in client.receive():
        file_data[stream_id] += chunk

    # we write to the files at once because disk access is expensive
    # instead we store them in memory (file_data) and as it has the whole data we write the files to disk
    for i in range(NUMBER_OF_FILES):
        file_name = ("large-" if i % 2 == 0 else "small-") + str(i // 2) + ".obj"
        with open(file_name, "wb") as f:
            f.write(file_data[i])
