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
    'aqi': ['AQI', None],
    "co": ['AQI_CO', None],
    "no2": ['AQI_NO2', None],
    "o3": ['AQI_O3', None],
    "pm10": ['AQI_PM10', None],
    "pm25": ['AQI_PM25', None],
    "qlty": ['AQI_QLTY', None],
    "so2": ['AQI_SO2', None],
}

DAY_FORECAST_TYPES =  {
    'sr': ['Day_SR', None],
    'ss': ['Day_SS', None],
    'mr': ['Day_MR', None],
    'ms': ['Day_MS', None],
    'Weather_d': ['Day_Weather_Day', None],
    'Weather_n': ['Day_Weather_Night', None],
    'hum': ['Day_HUM', None],
    'pop': ['Day_POP', None],
    'pres': ['Day_PRES', None],
    'maxTmp': ['Day_MaxTmp', None],
    'minTmp': ['Day_MinTmp', None],
    'uv': ['Day_UV', None],
    'vis': ['Day_VIS', None],
    'deg': ['Day_DEG', None],
    'dir': ['Day_DIR', None],
    'sc': ['Day_SC', None],
    'spd': ['Day_SPD', None],
}

HOUR_FORECAST_TYPE = {
    'Weather': ['Hour_Weather', None],
    'hum': ['Hour_HUM', None],
    'pop': ['Hour_POP', None],
    'pres': ['Hour_PRES', None],
    'Tmp': ['Hour_Tmp', None],
    'deg': ['Hour_DEG', None],
    'dir': ['Hour_DIR', None],
    'sc': ['Hour_SC', None],
    'spd': ['Hour_SPD', None],
}

NOW_FORECAST_TYPE = {
    'Weather': ['Now_Weather', None],
    'fl': ['Now_Fl', None],
    'hum': ['Now_HUM', None],
    'pcpn': ['Now_PCPN', None],
    'pres': ['Now_PRES', None],
    'Tmp': ['Now_Tmp', None],
    'vis': ['Now_VIS', None],
    'deg': ['Now_DEG', None],
    'dir': ['Now_DIR', None],
    'sc': ['Now_SC', None],
    'spd': ['Now_SPD', None],
}

SUGGESTION_FORECAST_TYPE = {
    'brf': ['Suggestion_BRF', None],
    'txt': ['Suggestion_TXT', None],
}
MODULE_SUGGESTION = vol.Schema({
    vol.Required(cv.string, default=[]):
        vol.All(cv.ensure_list, [vol.In(SUGGESTION_FORECAST_TYPE)]),
})

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
    vol.Required(CONF_SUGGESTION,default=[]): MODULE_SUGGESTION,
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
