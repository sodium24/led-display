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

from ..app_base import AppBase

cache = {}

class Weather(AppBase):
    """
    App to display the current weather
    """
    def run(self):
        """
        Main routine to display the weather
        """
        global cache

        units = self.app_config["units"]

        latitude = None
        longitude = None

        temperature = None
        weather_main = None
        weather_description = None
        weather_icon_url = None

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

        # update the display buffer with image data from the controls
        self.update()

        # redraw the display
        self.draw()

        if "lat_lon" not in cache:
            if "latitude" in self.app_config and "longitude" in self.app_config:
                latitude = self.app_config["latitude"]
                longitude = self.app_config["longitude"]
            if latitude is None and longitude is None:
                try:
                    ip_info = requests.get("https://ipapi.co/json/").json()
                    latitude = ip_info["latitude"]
                    longitude = ip_info["longitude"]
                except Exception as err:
                    print("Hit exception: %s" % err)
                    pass
        else:
            latitude = cache["lat_lon"][0]
            longitude = cache["lat_lon"][1]

        if latitude is None or longitude is None:
            print("Unknown lat/lon, cannot continue")
            return

        cache["lat_lon"] = [latitude, longitude]

        update_rate = 0.0
        needs_redraw = True

        while not self.stop_event.wait(update_rate):
            needs_refresh = False

            if "last_refresh" not in cache:
                needs_refresh = True
            else:
                if "weather_data" in cache:
                    if not needs_redraw:
                        needs_refresh = (time.time() - cache["last_refresh"]) > 60.0
                else:
                    needs_refresh = (time.time() - cache["last_refresh"]) > 30.0

            if needs_refresh:
                try:
                    print("Retrieving weather data for (%f, %f)" % (latitude, longitude))
                    weather_data = requests.get("https://openweathermap.org/data/2.5/onecall?lat=%f&lon=%f&units=%s&appid=439d4b804bc8187953eb36d2a8c26a02" % (latitude, longitude, units)).json()
                except Exception as err:
                    print("Hit exception: %s" % err)
                    pass
                cache["last_refresh"] = time.time()
                print("Weather data: %s" % weather_data)
                needs_redraw = True
            else:
                weather_data = cache.get("weather_data")

            if weather_data is None:
                print("Cannot retrieve weather")
                return

            if needs_redraw:

                cache["weather_data"] = weather_data

                temperature = weather_data.get("current", {}).get("temp")
                current_weather = weather_data.get("current", {}).get("weather", [])

                print("temperature: %f" % temperature)

                if len(current_weather) > 0:
                    print("weather: %s" % current_weather[0])
                    weather_main = current_weather[0]["main"]
                    weather_description = current_weather[0]["description"]
                    weather_icon_url = current_weather[0]["icon"]

                if weather_icon_url is not None:
                    weather_icon_url = "https://openweathermap.org/img/wn/%s@2x.png" % weather_icon_url
                    print("icon: %s" % weather_icon_url)

                if needs_refresh and weather_icon_url is not None:
                    icon_image = requests.get(weather_icon_url).content

                    with open("/tmp/weather_icon.png", "wb") as f:
                        f.write(icon_image)

                    image_control.filename = ""
                    
                    if os.path.exists("/tmp/weather_icon.png"):
                        image_control.filename = "/tmp/weather_icon.png"

                if temperature is not None:
                    if units == "metric":
                        temp_control.text = u"%d\u00b0C" % int(round(temperature))
                    else:
                        temp_control.text = u"%d\u00b0F" % int(round(temperature))

                if weather_main is not None:
                    weather_control.text = weather_main

                if weather_control.static:
                    update_rate = 1.0
                else:
                    update_rate = 0.1

                loading_control.enabled = False

            # update the display buffer with image data from the controls
            self.update()

            # redraw the display
            self.draw()

            needs_redraw = False

