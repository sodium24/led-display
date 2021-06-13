################################################################################
# cli.py
#-------------------------------------------------------------------------------
# Command line interface for interacting with the LED display over TCP.
# 
# By Malcolm Stagg
#
# Copyright (c) 2021 SODIUM-24, LLC
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
################################################################################

import cmd
from controllerclient import ControllerClient

controller = ControllerClient()

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
