################################################################################
# web_controller.py
#-------------------------------------------------------------------------------
# WIP web interace allowing remote control over the LED display.
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

import time
import threading
import sys
from flask import Flask, json, request, render_template
from multiprocessing import Process

from ..controller_base import ControllerBase
from .controller_client import ControllerClient

def web_process(ip, port, debug):
    """
    WIP website interface for the LED display
    """

    app = Flask(__name__)

    controller = ControllerClient()

    @app.route("/api/get_screen_order", methods=["GET"])
    def get_screen_order():
        result = controller.get_screen_order()

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/set_screen_order", methods=["POST"])
    def set_screen_order():
        result = controller.set_screen_order(request.get_json()["screen_order"])

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/save_screen_order", methods=["POST"])
    def set_screen_order():
        result = controller.save_screen_order(request.get_json()["screen_order"])

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/get_config", methods=["GET"])
    def get_config():
        result = controller.get_config()

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/set_config", methods=["POST"])
    def set_config():
        result = controller.set_config(request.get_json()["config"])

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/save_config", methods=["POST"])
    def save_config():
        result = controller.save_config(request.get_json()["config"])

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/get_state", methods=["GET"])
    def get_state():
        result = controller.get_state()

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/api/input_event", methods=["POST"])
    def input_event():
        result = controller.send_input_event(request.get_json()["inputEvent"])

        response = app.response_class(
            response=json.dumps(result),
            status=200,
            mimetype='application/json'
        )
        return response

    @app.route("/settings")
    def settings():
        config_data = controller.get_config()
        title = config_data.get("config", {}).get("settings", {}).get("title", "LED Display")
        return render_template('settings.html', title=title)

    @app.route("/")
    def index():
        config_data = controller.get_config()
        title = config_data.get("config", {}).get("settings", {}).get("title", "LED Display")
        return render_template('index.html', title=title)

    app.run(host=ip, port=port, debug=debug, use_reloader=False)

class WebController(ControllerBase):
    """
    Website controller for the LED display
    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the website controller
        """
        super(WebController, self).__init__(*args, **kwargs)

    def start(self):
        """
        Start the website interface based on configuration options
        """
        ip = self.config["settings"].get("webInterfaceIp", "0.0.0.0")
        port = self.config["settings"].get("webInterfacePort", 8080)
        debug = self.config["settings"].get("webInterfaceDebug", True)
        self.process = Process(target=web_process, args=(ip,port,debug))
        self.process.start()

    def stop(self):
        """
        Stop the website interface
        """
        self.process.terminate()
        self.process.join()

