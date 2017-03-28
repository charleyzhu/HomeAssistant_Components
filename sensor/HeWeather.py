import logging
import voluptuous as vol

from homeassistant.const import TEMP_CELSIUS ,CONF_LATITUDE, CONF_LONGITUDE, CONF_ELEVATION
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import (
    CONF_MONITORED_CONDITIONS,
    ATTR_ATTRIBUTION)
import requests


SENSOR_TYPES = {
    'aqi':['aqi',None],
    daily_forecast
    # 'symbol': ['Symbol', None],
    # 'precipitation': ['Precipitation', 'mm'],
    # 'temperature': ['Temperature', '°C'],
    # 'windSpeed': ['Wind speed', 'm/s'],
    # 'windGust': ['Wind gust', 'm/s'],
    # 'pressure': ['Pressure', 'hPa'],
    # 'windDirection': ['Wind direction', '°'],
    # 'humidity': ['Humidity', '%'],
    # 'fog': ['Fog', '%'],
    # 'cloudiness': ['Cloudiness', '%'],
    # 'lowClouds': ['Low clouds', '%'],
    # 'mediumClouds': ['Medium clouds', '%'],
    # 'highClouds': ['High clouds', '%'],
    # 'dewpointTemperature': ['Dewpoint temperature', '°C'],
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_MONITORED_CONDITIONS, default=['symbol']): vol.All(cv.ensure_list, vol.Length(min=1), [vol.In(SENSOR_TYPES.keys())]),
    vol.Optional(CONF_LATITUDE, default=0): cv.latitude,
    vol.Optional(CONF_LONGITUDE, default=0): cv.longitude,
    vol.Optional(CONF_ELEVATION, default=0): vol.Coerce(int),
})

_Log=logging.getLogger(__name__)

def setup_platform(hass, config, async_add_devices, discovery_info=None):
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    elevation = config.get(CONF_ELEVATION, hass.config.elevation or 0)

    if latitude == 0:
        _Log.error('Pls enter latitude!')
        return False

    if longitude == 0:
        _Log.error('Pls enter longitude!')
        return False

    if elevation == 0:
        _Log.error('Pls enter elevation!')
        return False

    coordinates = {'lat': str(latitude),
                   'lon': str(longitude),
                   'msl': str(elevation)}

    return False

class HeWeather(Entity):
    def __init__(self,coordinates):
        """Initialize the sensor."""
        self._coordinates = coordinates

    @property
    def name(self):
        """Return the name of the sensor."""

        city = self.getWeatherData("city")
        weather = self.getWeatherData("weather")
        return city + ' Temperature'

    @property
    def state(self):
        """Return the state of the sensor."""
        tmp = self.getWeatherData("temp2")
        return tmp

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return TEMP_CELSIUS


    def update(self):
