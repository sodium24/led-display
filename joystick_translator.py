class JoystickTranslator(object):
    def __init__(self):
        self.current_action = (None, 0.0)
        self.button_states = {}

    def on_joystick_press(self, button, button_states):
        self.button_states = dict(button_states)
        return None

    def on_joystick_release(self, button, button_states):
        input_event = None
        if button == "a" and self.button_states.get("a"):
            input_event = "select"
        if button == "b" and self.button_states.get("b"):
            input_event = "exit"
        self.button_states = dict(button_states)
        return input_event

    def on_joystick_axis(self, axis_states):
        input_event = None
        max_axis = None
        max_val = 0.0
        for axis in ["x", "y", "z", "rz", "hat0x", "hat0y"]:
            if abs(axis_states[axis]) > max_val:
                max_val = abs(axis_states[axis])
                max_axis = axis

        if max_axis is None:
            self.current_action = (None, 0.0)
            return input_event

        # print("Axis {}={}".format(axis, axis_states[axis]))
        if max_axis == self.current_action[0] and abs(axis_states[max_axis]) < 0.5:
            if self.current_action[0] in ["x", "z", "hat0x"] and self.current_action[1] > 0:
                input_event = "right"
            elif self.current_action[0] in ["x", "z", "hat0x"] and self.current_action[1] < 0:
                input_event = "left"
            elif self.current_action[0] in ["y", "rz", "hat0y"] and self.current_action[1] > 0:
                input_event = "down"
            elif self.current_action[0] in ["y", "rz", "hat0y"] and self.current_action[1] < 0:
                input_event = "up"
            self.current_action = (None, 0.0)
        elif abs(axis_states[max_axis]) > abs(self.current_action[1]) and abs(axis_states[max_axis]) > 0.5:
            self.current_action = (max_axis, axis_states[max_axis])

        return input_event
