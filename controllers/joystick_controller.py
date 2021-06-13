import os
import time
import fcntl
import joystick_device
import weakref
from controllerbase import ControllerBase

def has_js():
    for filename in os.listdir('/dev/input'):
        if filename.startswith('js'):
            return True

    return False

class JoystickController(ControllerBase):
    def __init__(self, *args, **kwargs):
        super(JoystickController, self).__init__(*args, **kwargs)

    def run(self):
        print("starting joystick controller...")

        while not self.exit_flag:
            while not has_js():
                time.sleep(1)

            jsdev = None

            try:
                jsdev = joystick_device.Joystick("/dev/input/js0")
                jsdev.on_press = self.send_joystick_press
                jsdev.on_release = self.send_joystick_release
                jsdev.on_axis = self.send_joystick_axis

                while has_js() and not jsdev.failed and not self.exit_flag:
                    time.sleep(1)
            except Exception as err:
                print("Exception" + str(err))
       
            if jsdev:
                jsdev.on_press = None
                jsdev.on_release = None
                jsdev.on_axis = None
                jsdev.terminate()

            time.sleep(1)
