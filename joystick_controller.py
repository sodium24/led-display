import os
import time
import fcntl
import controllers.joystick_device
import controllerclient

def has_js():
    for filename in os.listdir('/dev/input'):
        if filename.startswith('js'):
            return True

    return False

class JoystickController(object):
    def __init__(self, error_handler=None):
        self.current_action = (None, 0.0)
        self.controller = controllerclient.ControllerClient()
        self.controller.start()

        self.jsdev = controllers.joystick_device.Joystick("/dev/input/js0")
        self.jsdev.on_press = self.on_press
        self.jsdev.on_release = self.on_release
        self.jsdev.on_axis = self.on_axis
        self.exit_flag = False

    def terminate(self):
        self.exit_flag = True
        self.jsdev.on_press = None
        self.jsdev.on_release = None
        self.jsdev.on_axis = None
        self.jsdev.terminate()

    def on_press(self, button, button_states):
        self.controller.send_joystick_press(button, button_states)
        print("Button {} pressed".format(button))

    def on_release(self, button, button_states):
        self.controller.send_joystick_release(button, button_states)
        print("Button {} released".format(button))

    def on_axis(self, axis, axis_states):
        if not self.exit_flag:
            # print("Axis {}={}".format(axis, axis_states[axis]))
            if axis == self.current_action[0] and abs(axis_states[axis]) < 0.5:
                if self.current_action[0] in ["x", "z", "hat0x"] and self.current_action[1] > 0:
                    self.controller.send_input_event("right")
                elif self.current_action[0] in ["x", "z", "hat0x"] and self.current_action[1] < 0:
                    self.controller.send_input_event("left")
                elif self.current_action[0] in ["y", "rz", "hat0y"] and self.current_action[1] > 0:
                    self.controller.send_input_event("down")
                elif self.current_action[0] in ["y", "rz", "hat0y"] and self.current_action[1] < 0:
                    self.controller.send_input_event("up")
                self.current_action = (None, 0.0)
            elif abs(axis_states[axis]) > abs(self.current_action[1]) and abs(axis_states[axis]) > 0.5 and axis in ["x", "y", "z", "rz", "hat0x", "hat0y"]:
                self.current_action = (axis, axis_states[axis])

def main():
    joystick_controller = None

    try:
        joystick_controller = JoystickController()

        while has_js() and not joystick_controller.jsdev.failed:
            time.sleep(1)
    except Exception as err:
        print("Exception" + str(err))

    if joystick_controller:
        joystick_controller.terminate()

    time.sleep(1)

if __name__ == '__main__':

    locked_file_descriptor = open('/tmp/led-display-joystick.lock', 'w+')
    fcntl.lockf(locked_file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)

    while True:
        while not has_js():
            time.sleep(1)

        main()


