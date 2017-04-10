'''
WeatherChina　Developer by Charley
'''
import logging
import voluptuous as vol

from homeassistant.const import TEMP_CELSIUS
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv

import requests
import json


PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required('CityCode',default=[]):
        vol.All(cv.ensure_list(cv.string))
})

_Logger=logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the sensor platform."""

    # global _CityCodes
    cityCodes = config.get('CityCode')
    dev = []
    for code in cityCodes:
        # _Logger.info('[WeatherChina] init CityCode======>'+ code)
        dev.append(
            WeatherChina(code)
        )

    add_devices(dev)


class WeatherChina(Entity):
    """Representation of a Sensor."""

    def __init__(self,cityCode):
        """Initialize the sensor."""
        self._state = None
        self._cityCode = cityCode
        self._weatherData=None

    @property
    def name(self):
        """Return the name of the sensor."""

        city = self.getWeatherData("city")
        weather = self.getWeatherData("weather")
        return city + ' Temperature'

    @property
    def state(self):
        """Return the state of the sensor."""
        tmp = '%s'% self.getWeatherData("temp2")
        tmp = tmp[:-1]
        return tmp

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


    def update(self):
        """Fetch new state data for the sensor.

        This is the only method that should fetch new data for Home Assistant.
        """

        # _Logger.info("[WeatherChina] update =====>"+ self._cityCode)
        if self._cityCode == '':
            _Logger.error("[WeatherChina]: CityCode is nil")
            return

        urlStr = 'http://www.weather.com.cn/data/cityinfo/' + self._cityCode + '.html'
        # resp = None
        # try:

        # _Logger.info("[WeatherChina] updateUrl =====>" +urlStr)

        resp = requests.get(urlStr)
        if resp.status_code != 200:
            _Logger.error("http get Error code:" + resp.status_code)
            return
        resp.encoding = "utf-8"
        weatherDataStr=resp.text
        self._weatherData = json.loads(weatherDataStr)


    def getWeatherData(self,key):
        if  self._weatherData == None:
            return ""


        if not "weatherinfo" in self._weatherData:
            return ""

        weatherinfo = self._weatherData["weatherinfo"]

        if not key in weatherinfo:
            return ""

        return weatherinfo[key]
