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

CONF_AQI = 'aqi'
CONF_TODAY_FORECAST = 'ToDay_forecast'
CONF_TOMORROW_FORECAST = 'Tomorrow_forecast'
CONF_OFTERTOMORROW_FORECAST = 'OfterTomorrow_forecast'
CONF_1HOUR_FORECAST = '1Hour_forecast'
CONF_3HOUR_FORECAST = '3Hour_forecast'
CONF_6HOUR_FORECAST = '6Hour_forecast'
CONF_9HOUR_FORECAST = '9Hour_forecast'
CONF_12HOUR_FORECAST = '12Hour_forecast'
CONF_15HOUR_FORECAST = '15Hour_forecast'
CONF_18HOUR_FORECAST = '18Hour_forecast'
CONF_21HOUR_FORECAST = '21Hour_forecast'
CONF_NOW = 'now'
CONF_SUGGESTION = 'suggestion'

AQI_TYPES = {
    'aqi': ['aqi', None],
    "co": ['co', None],
    "no2": ['no2', None],
    "o3": ['o3', None],
    "pm10": ['pm10', None],
    "pm25": ['pm25', None],
    "qlty": ['qlty', None],
    "so2": ['so2', None],
}

DAY_FORECAST_TYPES =  {
    'sr': ['sr', None],
    'ss': ['ss', None],
    'mr': ['mr', None],
    'ms': ['ms', None],
    'Weather_d': ['Weather_d', None],
    'Weather_n': ['Weather_n', None],
    'hum': ['hum', None],
    'pop': ['pop', None],
    'pres': ['pres', None],
    'maxTmp': ['maxTmp', None],
    'minTmp': ['minTmp', None],
    'uv': ['uv', None],
    'vis': ['vis', None],
    'deg': ['deg', None],
    'dir': ['dir', None],
    'sc': ['sc', None],
    'spd': ['spd', None],
}

HOUR_FORECAST_TYPE = {
    'Weather': ['Weather', None],
    'hum': ['hum', None],
    'pop': ['pop', None],
    'pres': ['pres', None],
    'Tmp': ['Tmp', None],
    'deg': ['deg', None],
    'dir': ['dir', None],
    'sc': ['sc', None],
    'spd': ['spd', None],
}

NOW_FORECAST_TYPE = {
    'Weather': ['Weather', None],
    'fl': ['fl', None],
    'hum': ['hum', None],
    'pcpn': ['pcpn', None],
    'pres': ['pres', None],
    'Tmp': ['Tmp', None],
    'vis': ['vis', None],
    'deg': ['deg', None],
    'dir': ['dir', None],
    'sc': ['sc', None],
    'spd': ['spd', None],
}

SUGGESTION_FORECAST_TYPE = {
    'Weather': ['Weather', None],
    'fl': ['fl', None],
    'hum': ['hum', None],
    'pcpn': ['pcpn', None],
    'pres': ['pres', None],
    'Tmp': ['Tmp', None],
    'vis': ['vis', None],
    'deg': ['deg', None],
    'dir': ['dir', None],
    'sc': ['sc', None],
    'spd': ['spd', None],
}


MODULE_SCHEMA = vol.Schema({
    vol.Required(CONF_AQI,default=[]):vol.All(cv.ensure_list, [vol.In(AQI_TYPES)]),
    vol.Required(CONF_TODAY_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(DAY_FORECAST_TYPES)]),
    vol.Required(CONF_TOMORROW_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(DAY_FORECAST_TYPES)]),
    vol.Required(CONF_OFTERTOMORROW_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(DAY_FORECAST_TYPES)]),
    vol.Required(CONF_1HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_3HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_6HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_9HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_12HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_15HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_18HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_21HOUR_FORECAST,default=[]):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_NOW,default=[]):vol.All(cv.ensure_list, [vol.In(NOW_FORECAST_TYPE)]),
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_MONITORED_CONDITIONS): MODULE_SCHEMA,

    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_ELEVATION): vol.Coerce(int),
})

_Log=logging.getLogger(__name__)

def setup_platform(hass, config, async_add_devices, discovery_info=None):
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    elevation = config.get(CONF_ELEVATION, hass.config.elevation or 0)
    monitored_conditions = config[CONF_MONITORED_CONDITIONS]

    _Log.warning("monitored_conditions ==========>%s" % monitored_conditions)
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
        pass

    @property
    def state(self):
        """Return the state of the sensor."""
        pass

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        pass


    def update(self):
        pass
