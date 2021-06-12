import struct
import json

# Simple alternative to ZMQ since it takes forever to install on Raspberry Pi

class StreamMessage(object):
    @staticmethod
    def send(data_json, sock):
        str_data = json.dumps(data_json)
        binary_data = struct.pack("<I", len(str_data)) + str_data.encode()
        sock.send(binary_data)

    @staticmethod
    def recv(sock):
        length_buf = b''

        while len(length_buf) < 4:
            length_buf += sock.recv(4 - len(length_buf))

        length = struct.unpack("<I", length_buf)[0]

        data_buf = b''

        while len(data_buf) < length:
            data_buf += sock.recv(length - len(data_buf))

        return json.loads(data_buf.decode())
