################################################################################
# addons.py
#-------------------------------------------------------------------------------
# Extensions for adding apps and controllers.
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

from .apps.off import DisplayOff
from .apps.image_display import ImageDisplay
from .apps.slideshow import Slideshow
from .apps.menu import Menu
from .apps.snake import SnakeGame

from .controllers.controller_server import ControllerServer
from .controllers.joystick_controller import JoystickController
from .controllers.web_controller import WebController

# List of installed apps

apps = {
    "off": DisplayOff,
    "imageDisplay": ImageDisplay,
    "slideshow": Slideshow,
    "menu": Menu,
    "snake": SnakeGame,
}

# List of installed controllers

controllers = {
    "tcp": ControllerServer,
    "joystick": JoystickController,
    "web": WebController
}
