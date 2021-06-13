################################################################################
# stream_message.py
#------------------------------------------------------------------------------
# Class to serialize and deserialize JSON data to be sent over a TCP socket.
# This is a simple alternative to ZMQ, due to its extremely long installation
# times on a Raspberry Pi.
# 
# By Malcolm Stagg
#
# Copyright (c) 2021 SODIUM-24, LLC
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import struct
import json

class StreamMessage(object):
    """
    JSON serialization helper for a TCP interface
    """

    @staticmethod
    def send(data_json, sock):
        """
        Send serialized JSON data over a TCP socket
        """
        str_data = json.dumps(data_json)
        binary_data = struct.pack("<I", len(str_data)) + str_data.encode()
        sock.sendall(binary_data)

    @staticmethod
    def recv(sock):
        """
        Received serialized JSON data from a TCP socket
        """
        length_buf = b''

        while len(length_buf) < 4:
            length_buf += sock.recv(4 - len(length_buf))

        length = struct.unpack("<I", length_buf)[0]

        data_buf = b''

        while len(data_buf) < length:
            data_buf += sock.recv(length - len(data_buf))

        return json.loads(data_buf.decode())
