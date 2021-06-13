import socket
import sys
import os
import threading
import json
import socket
import weakref
from controllers.streammessage import StreamMessage

class ControllerServer(object):
    PORT = 1337

    def __init__(self, app=None):
        if app is None:
            self.app = None
        else:
            self.app = weakref.ref(app)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(("0.0.0.0", self.PORT))

        self.server_thread = None
        self.stop_flag = False
        self.handlers = {
            "ping": self.on_ping,
            "input_event": self.on_input_event,
            "joystick_press": self.on_joystick_press,
            "joystick_release": self.on_joystick_release,
            "get_state": self.on_get_state,
            "get_config": self.on_get_config,
            "set_config": self.on_set_config,
            "save_config": self.on_save_config,
        }

    def serve(self):

        self.socket.listen(1)

        while not self.stop_flag:
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

    def start(self):
        self.server_thread = threading.Thread(target=self.serve)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self):
        if self.server_thread:
            self.stop_flag = True
            self.socket.close()
            self.server_thread.join()
            self.server_thread = None

    def on_ping(self, data):
        return {}

    def on_get_state(self, data):
        if self.app is not None:
            app = self.app()
            return {"screenIndex": app.current_screen_index, "screenName": app.current_screen_name}
        else:
            return {}

    def on_get_config(self, data):
        return {"config": self.app().config}

    def on_set_config(self, data):
        self.app().config = data["config"]
        self.app().reload_running_app()
        return {}

    def on_save_config(self, data):
        self.app().config = data["config"]
        self.app().reload_running_app()
        self.app().save_config()
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
