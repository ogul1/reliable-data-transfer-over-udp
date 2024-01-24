import struct
import datetime
import hashlib
from constants import *


# returns the current timestamp
def get_current_timestamp():
    return datetime.datetime.utcnow().timestamp()


# calculates the checksum of the given packet
def calculate_checksum(data):
    return hashlib.md5(data).digest()


# a chunk header contains:
# sequence number --> sequence number of the packet
# timestamp --> timestamp that the packet was sent
# checksum --> checksum of the packet
# length --> length of the payload
# stream id --> indicates which file this chunk belongs to
# packs a packet to get it ready to send it over wire in network byte ordering
def pack_chunk(seq, stream_id, chunk, timestamp):
    length = len(chunk)
    checksum = calculate_checksum(chunk + bytes(str(timestamp), 'utf8') + bytes(str(length), 'utf8') + bytes(str(seq), 'utf8'))
    extra_space = DATA_PAYLOAD_SIZE - length
    return struct.pack(f'!Id16sII{length}s{extra_space}s', seq, timestamp, checksum, length, stream_id, chunk, b' ' * extra_space)


# unpacks a packet that is in network byte ordering and extracts the sequence number, timestamp, data, and stream id
def unpack_chunk(chunk):
    seq, timestamp, checksum, length, stream_id = struct.unpack(f'!Id16sII', chunk[:DATA_HEADER_SIZE])
    extra_space = DATA_PAYLOAD_SIZE - length
    data, _ = struct.unpack(f'!{length}s{extra_space}s', chunk[DATA_HEADER_SIZE:DATA_TOTAL_SIZE])
    if checksum == calculate_checksum(data + bytes(str(timestamp), 'utf8') + bytes(str(length), 'utf8') + bytes(str(seq), 'utf8')):
        return seq, timestamp, data, stream_id
    return None, None, None, None


# packs an ack to get it ready to send it over wire in network byte ordering
def pack_ack(seq):
    checksum = calculate_checksum(bytes(str(seq), 'utf8'))
    return struct.pack(f'!I16s', seq, checksum)


# unpacks an ack packet that is in network byte ordering and extracts the sequence number
def unpack_ack(ack):
    seq, checksum = struct.unpack(f'!I16s', ack)
    if checksum == calculate_checksum(bytes(str(seq), 'utf8')):
        return seq
    return None
