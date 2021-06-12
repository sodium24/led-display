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
        self.running = False
        self.current_app = None
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

        if not handled and self.current_app is not None:
            handled = self.current_app.on_input_event(input_event)

        if not handled:
            if input_event == "right":
                self.screen_index += 1
                self.screen_index %= len(self.config["screenOrder"])
                if self.current_app is not None:
                    self.current_app.stop()
                handled = True
            elif input_event == "left":
                self.screen_index -= 1
                self.screen_index %= len(self.config["screenOrder"])
                if self.current_app is not None:
                    self.current_app.stop()
                handled = True

        return handled

    def start_app(self, index):
        self.current_screen_index = self.screen_index = index
        screen_name = self.config["screenOrder"][self.screen_index]
        self.start_app_by_name(screen_name)

    def start_app_by_name(self, screen_name):
        self.current_screen_name = screen_name
        screen_app = self.config["screens"][screen_name]
        screen_class = addons.apps[screen_app["app"]]
        app_config = screen_app.get("config", {})
        self.current_app = screen_class(self.config, app_config, self.loaded_fonts, self.matrix)
        self.running = True
        print("Starting app for screen " + screen_name)
        print("Press CTRL-C to stop...")
        self.current_app.start()
        print("Execution complete")
        self.running = False

    def wait_for_complete(self):
        self.current_app.stop()
        while self.running:
            time.sleep(1)

    def run(self):
        while True:
            if self.current_screen_index != self.screen_index or self.restart_app:
                self.restart_app = False
                try:
                    self.start_app(self.screen_index)
                except Exception as err:
                    print("Exception while running app: %s" % err)
                    self.running = False
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
