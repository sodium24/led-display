import addons
import sys
import json
import threading
import time

class MainApp(object):
    def __init__(self, config):
        self.config = config
        self.screen_index = 0
        self.loaded_fonts = {}
        self.running = False
        self.current_app = None

    def start_app(self):
        screen_name = self.config["screenOrder"][self.screen_index]
        screen_app = self.config["screens"][screen_name]
        screen_class = addons.apps[screen_app["app"]]
        app_config = screen_app["config"]
        self.current_app = screen_class(self.config, app_config, self.loaded_fonts)
        self.running = True
        self.current_app.start()
        self.running = False

    def wait_for_complete(self):
        self.current_app.stop()
        while self.running:
            time.sleep(1)

    def run(self):
        self.start_app()

        try:
            print("Press CTRL-C to stop sample")
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting\n")
            self.wait_for_complete()

def main():
    if len(sys.argv) < 2:
        print("Usage: %s <config_json_file>" % sys.argv[0])
        exit(1)

    with open(sys.argv[1]) as json_file:
        json_config = json.loads(json_file.read())

    main_app = MainApp(json_config)
    main_app.run()

if __name__ == "__main__":
    main()
