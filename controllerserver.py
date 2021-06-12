import socket
import sys
import os
import threading
import select
import json
import weakref

class ControllerServer(object):
    def __init__(self, app=None):
        if app is None:
            self.app = None
        else:
            self.app = weakref.ref(app)

        # create a domain socket to connect to controller(s)
        server_address = "/tmp/led-display-control"
        try:
            os.unlink(server_address)
        except OSError:
            if os.path.exists(server_address):
                raise
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.sock.bind(server_address)
        os.chmod(server_address, 0o777)
        self.server_thread = None
        self.stop_flag = False
        self.handlers = {
            "ping": self.on_ping,
            "input_event": self.on_input_event,
            "joystick_press": self.on_joystick_press,
            "joystick_release": self.on_joystick_release,
        }

    def serve(self):
        poll = select.poll()
        poll.register(self.sock, select.POLLIN)
        while not self.stop_flag:
            if len(poll.poll(100)) > 0:
                command, client_address = self.sock.recvfrom(65536)
                if command:
                    command = json.loads(command.decode())
                    print("server", command)
                    try:
                        response = self.handlers[command["type"]](command)
                        self.sock.sendto(json.dumps({"id": command["id"]}).encode(), client_address)
                    except KeyError as err:
                        print("Command not found: " + err)

    def start(self):
        self.server_thread = threading.Thread(target=self.serve)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        if self.server_thread:
            self.stop_flag = True
            self.sock.close()
            self.server_thread.join()
            self.server_thread = None

    def on_ping(self, data):
        return {}

    def on_input_event(self, data):
        handled = False
        if self.app is not None:
            handled = self.app().on_input_event(data["input_event"])
        return {"handled": handled}

    def on_joystick_press(self, data):
        handled = False
        if self.app is not None:
            handled = self.app().on_joystick_press(data["button"], data["button_states"])
        return {"handled": handled}

    def on_joystick_release(self, data):
        handled = False
        if self.app is not None:
            handled = self.app().on_joystick_release(data["button"], data["button_states"])
        return {"handled": handled}
