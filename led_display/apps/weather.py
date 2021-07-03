################################################################################
# weather.py
#-------------------------------------------------------------------------------
# Weather app based on openweathermap.org.
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
import datetime
import os
import requests
import threading

from ..app_base import AppBase

class WeatherUpdater(object):
    """
    Class to update weather information periodically
    """
    def __init__(self):
        self.config = {
            "latitude": None,
            "longitude": None,
            "units": "imperial"
        }

        self.latitude = None
        self.longitude = None
        self.last_refresh = None
        self.weather_data = None
        self.temperature = None
        self.current_weather = None
        self.weather_main = None
        self.weather_description = None
        self.weather_icon_type = None
        self.weather_icon_type = None
        self.weather_icon_url = None
        self.weather_icon_filename = None

        self.update_weather_event = threading.Event()
        self.stop_event = threading.Event()

        self._update_config()

    def set_config(self, config):
        if config != self.config:
            self.config.update(config)
            self._update_config()

    def start(self):
        self.weather_update_thread = threading.Thread(target=self._do_weather_update)
        self.weather_update_thread.daemon = True
        self.weather_update_thread.start()

    def stop(self):
        if self.weather_update_thread is not None:
            self.stop_event.set()
            self.update_weather_event.set()
            self.weather_update_thread.join()
            self.weather_update_thread = None

    def update(self):
        self.update_weather_event.set()

    def _do_weather_update(self):
        while True:
            self.update_weather_event.wait()
            if self.stop_event.is_set():
                break

            try:
                needs_refresh = False

                if self.last_refresh is None:
                    needs_refresh = True
                else:
                    if self.weather_data is not None:
                        needs_refresh = (time.time() - self.last_refresh) > 60.0
                    else:
                        needs_refresh = (time.time() - self.last_refresh) > 30.0

                if needs_refresh:
                    try:
                        print("Retrieving weather data for (%f, %f)" % (self.latitude, self.longitude))
                        self.weather_data = requests.get("https://openweathermap.org/data/2.5/onecall?lat=%f&lon=%f&units=%s&appid=439d4b804bc8187953eb36d2a8c26a02" % (self.latitude, self.longitude, self.units)).json()
                    except Exception as err:
                        print("Hit exception: %s" % err)

                    print("Weather data: %s" % self.weather_data)

                    self.temperature = self.weather_data.get("current", {}).get("temp")
                    self.current_weather = self.weather_data.get("current", {}).get("weather", [])

                    print("temperature: %f" % self.temperature)

                    if len(self.current_weather) > 0:
                        print("weather: %s" % self.current_weather[0])
                        self.weather_main = self.current_weather[0]["main"]
                        self.weather_description = self.current_weather[0]["description"]
                        self.weather_icon_type = self.current_weather[0]["icon"]

                    if self.weather_icon_type is not None:
                        weather_icon_filename = "/tmp/%s.png" % self.weather_icon_type

                        self.weather_icon_url = "https://openweathermap.org/img/wn/%s@2x.png" % self.weather_icon_type
                        print("icon: %s" % self.weather_icon_url)

                        if not os.path.exists(weather_icon_filename):
                            icon_image = requests.get(self.weather_icon_url).content

                            with open("/tmp/%s.png" % self.weather_icon_type, "wb") as f:
                                f.write(icon_image)

                        self.weather_icon_filename = weather_icon_filename

                    self.last_refresh = time.time()

                self.update_weather_event.clear()

            except Exception as err:
                print("Hit exception: %s" % err)
                time.sleep(5.0)

    def _update_config(self):
        self.units = self.config.get("units", "imperial")
        self._get_location()
        self.update_weather_event.set()

    def _get_location(self):
        if self.config.get("latitude") is not None and self.config.get("longitude") is not None:
            self.latitude = self.config["latitude"]
            self.longitude = self.config["longitude"]
        else:
            try:
                ip_info = requests.get("https://ipapi.co/json/").json()
                self.latitude = ip_info["latitude"]
                self.longitude = ip_info["longitude"]
            except Exception as err:
                print("Hit exception: %s" % err)
                pass

weather_updater = WeatherUpdater()
weather_updater.start()

class Weather(AppBase):
    """
    App to display the current weather
    """
    def __init__(self, config, app_config, *args, **kwargs):
        """
        Initialize the app
        """
        super(Weather, self).__init__(config, app_config, *args, **kwargs)

        global weather_updater

        weather_updater.set_config(app_config)
        weather_updater.update()

    def run(self):
        """
        Main routine to display the weather
        """
        image_control = self.create_control("image", "image_0")
        image_control.x = 0
        image_control.y = 0
        image_control.width = self.offscreen_canvas.width
        image_control.height = self.offscreen_canvas.height

        temp_control = self.create_control("text", "text_temperature")
        temp_control.font = "7x13"
        temp_control.color = [255, 255, 255]
        temp_control.text = ""
        temp_control.x = self.offscreen_canvas.width/2
        temp_control.y = 15
        temp_control.align = "center"
        temp_control.scroll = "none"

        weather_control = self.create_control("text", "text_weather")
        weather_control.font = "6x9"
        weather_control.color = [255, 255, 255]
        weather_control.text = ""
        weather_control.x = self.offscreen_canvas.width/2
        weather_control.y = self.offscreen_canvas.height-5
        weather_control.align = "center"
        weather_control.scroll = "auto"

        loading_control = self.create_control("text", "text_loading")
        loading_control.font = "6x9"
        loading_control.color = [255, 255, 255]
        loading_control.text = "loading..."
        loading_control.x = self.offscreen_canvas.width/2
        loading_control.y = self.offscreen_canvas.height/2
        loading_control.align = "center"
        loading_control.scroll = "auto"

        global weather_updater

        last_refresh = None
        update_rate = 0.1

        while not self.stop_event.wait(update_rate):
            weather_updater.update()

            if weather_updater.last_refresh != last_refresh:
                loading_control.enabled = False
                last_refresh = weather_updater.last_refresh

                if weather_updater.weather_icon_filename is not None:
                    if os.path.exists(weather_updater.weather_icon_filename):
                        image_control.filename = weather_updater.weather_icon_filename
                
                if weather_updater.temperature is not None:
                    if weather_updater.units == "metric":
                        temp_control.text = u"%d\u00b0C" % int(round(weather_updater.temperature))
                    else:
                        temp_control.text = u"%d\u00b0F" % int(round(weather_updater.temperature))

                    if weather_updater.weather_main is not None:
                        weather_control.text = weather_updater.weather_main

                if weather_updater.weather_icon_filename is not None and os.path.exists(weather_updater.weather_icon_filename):
                    image_control.filename = weather_updater.weather_icon_filename

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

            if weather_control.static:
                update_rate = 1.0
            else:
                update_rate = 0.1

