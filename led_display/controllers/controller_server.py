################################################################################
# controller_server.py
#-------------------------------------------------------------------------------
# TCP server class to allow client connections for interacting with the LED
# display.
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
import socket
import sys
import os
import threading
import json
import socket
import weakref
from ..controller_base import ControllerBase
from .stream_message import StreamMessage

class ControllerServer(ControllerBase):
    """
    TCP Server class to enable interacting with the LED display
    """

    PORT = 1337

    def __init__(self, *args, **kwargs):
        """
        Initialize the server
        """
        super(ControllerServer, self).__init__(*args, **kwargs)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("0.0.0.0", self.PORT))

        self.handlers = {
            "ping": self.on_ping,
            "input_event": self.on_input_event,
            "joystick_press": self.on_joystick_press,
            "joystick_release": self.on_joystick_release,
            "joystick_axis": self.on_joystick_axis,
            "get_state": self.on_get_state,
            "get_config": self.on_get_config,
            "set_config": self.on_set_config,
            "save_config": self.on_save_config,
        }

    def run(self):
        """
        Main server run loop routine
        """
        self.socket.listen(1)

        while not self.stop_event.is_set():
            conn, addr = self.socket.accept()            
            message = StreamMessage.recv(conn)
            if message:
                print("server", message)
                try:
                    response = self.handlers[message["type"]](message)
                    StreamMessage.send(response, conn)
                except KeyError as err:
                    print("Command not found: %s" % err)
            conn.close()

    def stop(self):
        """
        Stop a running controller
        """
        self.socket.close()
        super(ControllerServer, self).stop()

    def on_ping(self, data):
        """
        Handle a ping request from the client
        """
        return {}

    def on_get_state(self, data):
        """
        Handle an app state request from the client
        """
        return self.get_state()

    def on_get_config(self, data):
        """
        Handle a retrieve app configuration request from the client
        """
        return {"config": self.get_config()}

    def on_set_config(self, data):
        """
        Handle a set app configuration request from the client
        """
        self.set_config(data["config"])
        return {}

    def on_save_config(self, data):
        """
        Handle a set and save app configuration request from the client
        """
        self.save_config(data["config"])
        return {}

    def on_input_event(self, data):
        """
        Handle input event injection from the client
        """
        handled = self.send_input_event(data["input_event"])
        return {"handled": handled}

    def on_joystick_press(self, data):
        """
        Handle joystick button press injection from the client
        """
        handled = self.send_joystick_press(data["button"], data["button_states"])
        return {"handled": handled}

    def on_joystick_release(self, data):
        """
        Handle joystick button release injection from the client
        """
        handled = self.send_joystick_release(data["button"], data["button_states"])
        return {"handled": handled}

    def on_joystick_axis(self, data):
        """
        Handle joystick axis event injection from the client
        """
        handled = self.send_joystick_axis(data["axis_states"])
        return {"handled": handled}
