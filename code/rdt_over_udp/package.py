from constants import *


# this class contains the structure of a packet object
# sequence number is the order of the packet inside a window
# stream_id is the identifier of which file this packet belongs to
# chunk is the payload
# state is the current state of the packet in the finite state machine logic
# timestamp is the time that the packet was sent
class Package:
    def __init__(self, seq, stream_id=None, chunk=None, state=WAITING, timestamp=None):
        self.seq = seq
        self.stream_id = stream_id
        self.chunk = chunk
        self.state = state
        self.timestamp = timestamp
