import addons
import sys
import json
import threading
import time
import appbase
import controllerserver
import os

class MainApp(appbase.AppBase):
    def __init__(self, json_file):
        self.loaded_fonts = {}
        self.json_file = json_file
        with open(self.json_file) as f:
            config = json.loads(f.read())

        super(MainApp, self).__init__(config, config, self.loaded_fonts)

        self.config = config
        self.current_screen_index = -1
        self.current_screen_name = ""
        self.screen_index = 0
        self.controller = controllerserver.ControllerServer(self)
        self.controller.start()
        self.restart_app = False

    def save_config(self):
        try:
            os.unlink(self.json_file + ".bak")
        except Exception:
            pass
        try:
            os.rename(self.json_file, self.json_file + ".bak")
        except Exception:
            pass
        with open(self.json_file, "w") as f:
            f.write(json.dumps(self.config, indent=4))

    def on_input_event(self, input_event):
        handled = False

        if not handled and self.running_app is not None:
            handled = self.running_app.on_input_event(input_event)

        if not handled:
            if input_event == "right":
                self.screen_index += 1
                self.screen_index %= len(self.config["screenOrder"])
                self.stop_running_app()
                handled = True
            elif input_event == "left":
                self.screen_index -= 1
                self.screen_index %= len(self.config["screenOrder"])
                self.stop_running_app()
                handled = True

        return handled

    def enter_sleep_mode(self):
        if self.running_app:
            def on_app_exit(app):
                self.matrix.Clear()

            self.running_app.on_app_exit = on_app_exit
            self.stop_running_app()
        else:
            self.matrix.Clear()

    def stop_running_app(self):
        if self.running_app is not None:
            self.running_app.stop()

    def reload_running_app(self):
        self.restart_app = True

    def _start_app(self, index):
        self.current_screen_index = self.screen_index = index
        screen_name = self.config["screenOrder"][self.screen_index]
        self.current_screen_name = screen_name
        self._start_app_by_name(screen_name)

    def wait_for_complete(self):
        while self.running_app:
            time.sleep(1)

    def run(self):
        while True:
            if self.current_screen_index != self.screen_index or self.restart_app:
                self.stop_running_app()
                self.restart_app = False
                self._start_app(self.screen_index)
            else:
                time.sleep(1)

def main():
    if len(sys.argv) < 2:
        print("Usage: %s <config_json_file>" % sys.argv[0])
        exit(1)

    main_app = MainApp(sys.argv[1])
    main_app.start()

if __name__ == "__main__":
    main()
