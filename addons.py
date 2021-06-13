from apps.off import DisplayOff
from apps.image_display import ImageDisplay
from apps.slideshow import Slideshow
from apps.menu import Menu
from controllers.controllerserver import ControllerServer
from controllers.joystick_controller import JoystickController

# List of installed apps

apps = {
    "off": DisplayOff,
    "imageDisplay": ImageDisplay,
    "slideshow": Slideshow,
    "menu": Menu,
}

# List of installed controllers, not including ones which run as a separate process (like web)

controllers = {
    "tcp": ControllerServer,
    "joystick": JoystickController,
}
