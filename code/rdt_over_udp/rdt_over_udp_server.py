import socket
from collections import deque
from package import *
from package_operations import *

# Selective Repeat sender is implemented below. Details taken from the book
# Cumulative ACKs and fast retransmit mechanism are also implemented.

# If data is received, and the next sequence number is within the sender window, send the data
# If data is received, and the next sequence number is out of the sender window, buffer the data

# Each packet has its own logical timer, a single packet will be retransmitted in case of timeout

# If an ACK is received, and it is in the sender window, mark that packet as received
# If the ACK sequence number is equal to send_base, move the sender window forward until the first unacknowledged packet
# If the window moves, there are new packets which are not transmitted. Then, transmit them.


class rdt_over_udp_server:
    def __init__(self, server_host, server_port, client_host, client_port, data):
        self.client = (client_host, client_port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind((server_host, server_port))

        # whenever there is no data to receive currently just continue executing the next lines
        self.socket.setblocking(False)

        # increase the buffer size to 0.4mb
        # by default the buffers have a size of 0.2mb so effectively this is doubling the send and receive buffers
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 425984)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 425984)

        self.data = data

        self.seq_num = 0
        self.stream_id = 0
        self.duplicate_count = 0

        self.waiting_window = deque()
        self.sent_window = deque()

        self.make_window()

    def make_window(self):
        while len(self.waiting_window) + len(self.sent_window) < WINDOW_SIZE:
            try:
                # get the next chunk of data from upper layer
                chunk = next(self.data)

                # append the next package to the window, with state WAITING
                self.waiting_window.append(Package(self.seq_num, self.stream_id, chunk, WAITING, None))

                # increase the sequence number by one
                self.seq_num += 1

                # end of file reached to increment stream_id by 1
                # stream_id is used to distinguish between files
                if len(chunk) == 0:
                    self.stream_id += 1

            except StopIteration:
                break

    def send(self):
        # while we have data to send
        while self.waiting_window or self.sent_window:
            # if we have packets that are waiting to be transmitted, send one of them here and add it to the sent window
            if self.waiting_window:
                packet = self.waiting_window.popleft()
                packet.timestamp = get_current_timestamp()

                self.sent_window.append(packet)

                self.socket.sendto(pack_chunk(packet.seq, packet.stream_id, packet.chunk, packet.timestamp), self.client)

            # go into the finite state machine logic
            self.fsm()

        # close the socket when we are done
        self.socket.close()

    def fsm(self):
        try:
            # receive the ACK packet from the client and unpack it
            ack, client_address = self.socket.recvfrom(ACK_SIZE)
            ack_seq = unpack_ack(ack)

            # if the sequence number of the ACK is <= of the first sequence number in the window, then we know that
            # this ACK packet indicates that the first packet in the window was lost or delivered in a different order
            # once it detects 3 duplicate ACKs, it will resend the first packet in the window
            if ack_seq <= self.sent_window[0].seq:
                self.duplicate_count += 1
                if self.duplicate_count == 3:
                    self.socket.sendto(pack_chunk(self.sent_window[0].seq, self.sent_window[0].stream_id, self.sent_window[0].chunk, self.sent_window[0].timestamp), self.client)
                    self.duplicate_count = 0
                return
            self.duplicate_count = 0

            # this is the cumulative ACK logic.
            # when we receive an ack with sequence number greater than the first element of the window, we know that
            # all the packets before that sequence number were delivered to the client. thus we move the window
            # until the first sequence number in the window is equal to ack_seq
            while self.sent_window and ack_seq > self.sent_window[0].seq:
                self.sent_window.popleft()

        except BlockingIOError:
            pass

        for packet in self.sent_window:
            # if the timout occurs, we retransmit that packet
            if get_current_timestamp() - packet.timestamp > RETRANSMISSION_TIMEOUT:
                packet.timestamp = get_current_timestamp()
                self.socket.sendto(pack_chunk(packet.seq, packet.stream_id, packet.chunk, packet.timestamp), self.client)

        # fill the window and set their state to WAITING
        self.make_window()
