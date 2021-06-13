import socket
import sys
import os
import threading
import socket
import json
import time
from streammessage import StreamMessage

class ControllerClient(object):
    PORT = 1337

    def __init__(self, ip="localhost"):
        self.ip = ip

    def check_connected(self):
        return self.send_sync_command("ping", {})

    def get_state(self):
        return self.send_sync_command("get_state", {})

    def get_config(self):
        return self.send_sync_command("get_config", {})

    def set_config(self, config):
        return self.send_sync_command("set_config", {"config": config})

    def save_config(self, config):
        return self.send_sync_command("save_config", {"config": config})

    def send_input_event(self, input_event):
        return self.send_sync_command("input_event", {"input_event": input_event})

    def send_joystick_press(self, button, button_states):
        return self.send_sync_command("joystick_press", {"button": button, "button_states": button_states})

    def send_joystick_release(self, button, button_states):
        return self.send_sync_command("joystick_release", {"button": button, "button_states": button_states})

    def send_joystick_axis(self, axis_states):
        return self.send_sync_command("joystick_axis", {"axis_states": axis_states})

    def send_sync_command(self, command_type, data):
        data["type"] = command_type
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.ip, self.PORT))
        StreamMessage.send(data, sock)
        response = StreamMessage.recv(sock)
        sock.close()
        return response

