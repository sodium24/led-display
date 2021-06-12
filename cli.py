import controllerclient
import cmd

controller = controllerclient.ControllerClient()
controller.start()

class LedDisplayCli(cmd.Cmd):
    intro = "LED Display CLI\n\nType help or ? to list commands.\n"
    prompt = 'led-display> '
    file = None

    def do_left(self, arg):
        'User input event: left'
        controller.send_input_event("left")

    def do_right(self, arg):
        'User input event: right'
        controller.send_input_event("right")

    def do_up(self, arg):
        'User input event: up'
        controller.send_input_event("up")

    def do_down(self, arg):
        'User input event: down'
        controller.send_input_event("down")

    def do_select(self, arg):
        'User input event: select'
        controller.send_input_event("select")

if __name__ == '__main__':
    LedDisplayCli().cmdloop()
