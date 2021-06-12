import socket
import sys
import os
import threading
import select
import json
import time

class ControllerClient(object):
    TIMEOUT = 1.0

    def __init__(self):
        # Connect to the server's domain socket
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
        self.server_address = "/tmp/led-display-control"
        client_address = "/tmp/led-display-control-" + str(os.getpid())
        try:
            os.unlink(client_address)
        except OSError:
            if os.path.exists(client_address):
                raise
        self.sock.bind(client_address)
        os.chmod(client_address, 0o777)
        self.id = 0
        self.awaiting_response = {}
        self.server_thread = None
        self.stop_flag = False

    def serve(self):
        poll = select.poll()
        poll.register(self.sock, select.POLLIN)
        while not self.stop_flag:
            if len(poll.poll(100)) > 0:
                command, client_address = self.sock.recvfrom(65536)
                if command:
                    command = json.loads(command.decode())
                    command_id = command["id"]
                    on_success = self.awaiting_response[command_id]["on_success"]
                    if on_success:
                        on_success()
                    del self.awaiting_response[command_id]
                    print("response", command)

            now = time.time()
            to_delete = []
            for command_id in self.awaiting_response:
                if now - self.awaiting_response[command_id]["time"] > self.TIMEOUT:
                    on_failure = self.awaiting_response[command_id]["on_failure"]
                    if on_failure:
                        on_failure()
                    to_delete += [command_id]

            for command_id in to_delete:
                del self.awaiting_response[command_id]

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

    def check_connected(self, on_success=None, on_failure=None):
        self.send_sync_command("ping", 
            {}, 
            on_success=on_success,
            on_failure=on_failure)

    def send_input_event(self, input_event, on_success=None, on_failure=None):
        self.send_sync_command("input_event",
            {"input_event": input_event},
            on_success=on_success, 
            on_failure=on_failure)

    def send_sync_command(self, command_type, data, on_success=None, on_failure=None):
        data["type"] = command_type
        data["id"] = self.id
        self.sock.sendto(json.dumps(data).encode(), self.server_address)
        self.awaiting_response[self.id] = {
            "time": time.time(),
            "on_success": on_success,
            "on_failure": on_failure,
        }
        self.id += 1

