import socket
from collections import deque
from package import *
from package_operations import *


# Selective Repeat receiver is implemented below. Details taken from the book.

# Packet with sequence number [rcv_base, rcv_base+N-1] is correctly received. Send selective ACK. If its sequence number
# is equal to rcv_base, then any previously buffered and consecutively numbered packets are delivered to the application
# layer. Receive window moves forward by the number of packets delivered to the application layer.

# Packet with sequence number [rcv_base-N, rcv_base-1] is correctly received. Send selective ACK.

# Otherwise, ignore.


class rdt_over_udp_client:
    def __init__(self, client_host, client_port):
        self.client_host = client_host
        self.client_port = client_port

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((self.client_host, self.client_port))

        # whenever there is no data to receive currently just continue executing the next lines
        self.socket.setblocking(False)

        # increase the buffer size to 0.4mb
        # by default the buffers have a size of 0.2mb so effectively this is doubling the send and receive buffers
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 425984)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 425984)

        # transmission of the file with <stream_id> ended or not
        self.transmission_ended = [False for _ in range(NUMBER_OF_FILES)]

        self.seq_num = 0

        # window is a deque that contains the packets.
        # packets have two important fields:
        # sequence number and stream id
        # sequence number determines the order of the packets and stream id determines which file this packet belongs to
        self.window = deque()

        # fill the window when starting
        self.make_window()

    def make_window(self):
        # fill the window in increasing order of sequence numbers
        while len(self.window) < WINDOW_SIZE:
            self.window.append(Package(self.seq_num))
            self.seq_num += 1

    def continue_receiving(self):
        # if there is a stream_id that hasn't finished transmitting, then the while loop should keep on going
        for stream_id in range(NUMBER_OF_FILES):
            if not self.transmission_ended[stream_id]:
                return True
        return False

    def receive(self):
        # while we have to continue receiving
        while self.continue_receiving():
            try:
                # receive data from the server and unpack it
                chunk, server_address = self.socket.recvfrom(DATA_TOTAL_SIZE)
                seq, timestamp, data, stream_id = unpack_chunk(chunk)

                if data is not None:
                    # if this packet has the expected sequence number then start delivering packets to the upper layer
                    # starting from the beginning of the window, while there are packets that are RECEIVED deliver
                    # them to the upper layer
                    if seq == self.window[0].seq:
                        self.window[0].chunk = data
                        self.window[0].timestamp = timestamp
                        self.window[0].stream_id = stream_id
                        self.window[0].state = RECEIVED

                        while self.window:
                            if self.window[0].stream_id is not None and self.transmission_ended[self.window[0].stream_id]:
                                self.window.popleft()
                                continue

                            # if the first element of the window is not RECEIVED
                            if self.window[0].state != RECEIVED:
                                break

                            # if we have reached the last chunk of the file, (b'' has length 0)
                            if len(self.window[0].chunk) == 0:
                                # transmission ended for this file so set the corresponding entry to True and
                                # pop from the window
                                self.transmission_ended[self.window[0].stream_id] = True
                                self.window.popleft()
                                continue

                            # yield current packet's stream id and its corresponding data
                            yield self.window[0].stream_id, self.window[0].chunk

                            # pop that packet from the window because it is delivered to the upper layer
                            self.window.popleft()

                            # expand the window
                            self.window.append(Package(self.seq_num))
                            self.seq_num += 1
                    else:
                        for packet in self.window:
                            # mark WAITING packet as RECEIVED
                            if packet.seq == seq and packet.state == WAITING:
                                packet.chunk = data
                                packet.timestamp = timestamp
                                packet.stream_id = stream_id
                                packet.state = RECEIVED

                # send the next expected packet number as ack
                ack = pack_ack(self.window[0].seq)
                self.socket.sendto(ack, server_address)

            except BlockingIOError:
                pass

        # close this socket when we are done
        self.socket.close()
