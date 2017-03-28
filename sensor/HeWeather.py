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

# AQI_TYPE = {
#     'aqi':['aqi',None],
#     "co" :['co',None],
#     "no2" :['no2',None],
#     "o3" :['o3',None],
#     "pm10" :['pm10',None],
#     "pm25" :['pm25',None],
#     "qlty" :['qlty',None],
#     "so2" :['so2',None],
# }

# CONF_MODULES = 'modules'

# SENSOR_TYPES = {
#     'temperature': ['Temperature', TEMP_CELSIUS, 'mdi:thermometer'],
#     'co2': ['CO2', 'ppm', 'mdi:cloud'],
#     'pressure': ['Pressure', 'mbar', 'mdi:gauge'],
#     'noise': ['Noise', 'dB', 'mdi:volume-high'],
#     'humidity': ['Humidity', '%', 'mdi:water-percent'],
#     'rain': ['Rain', 'mm', 'mdi:weather-rainy'],
#     'sum_rain_1': ['sum_rain_1', 'mm', 'mdi:weather-rainy'],
#     'sum_rain_24': ['sum_rain_24', 'mm', 'mdi:weather-rainy'],
#     'battery_vp': ['Battery', '', 'mdi:battery'],
#     'battery_lvl': ['Battery_lvl', '', 'mdi:battery'],
#     'min_temp': ['Min Temp.', TEMP_CELSIUS, 'mdi:thermometer'],
#     'max_temp': ['Max Temp.', TEMP_CELSIUS, 'mdi:thermometer'],
#     'WindAngle': ['Angle', '', 'mdi:compass'],
#     'WindAngle_value': ['Angle Value', 'º', 'mdi:compass'],
#     'WindStrength': ['Strength', 'km/h', 'mdi:weather-windy'],
#     'GustAngle': ['Gust Angle', '', 'mdi:compass'],
#     'GustAngle_value': ['Gust Angle Value', 'º', 'mdi:compass'],
#     'GustStrength': ['Gust Strength', 'km/h', 'mdi:weather-windy'],
#     'rf_status': ['Radio', '', 'mdi:signal'],
#     'rf_status_lvl': ['Radio_lvl', '', 'mdi:signal'],
#     'wifi_status': ['Wifi', '', 'mdi:wifi'],
#     'wifi_status_lvl': ['Wifi_lvl', 'dBm', 'mdi:wifi']
# }

SENSOR_TYPES = {
    'aqi': ['aqi', None],
    "co": ['co', None],
    "no2": ['no2', None],
    "o3": ['o3', None],
    "pm10": ['pm10', None],
    "pm25": ['pm25', None],
    "qlty": ['qlty', None],
    "so2": ['so2', None],
    # 'aqi':('aqi','co'),
    # 'ToDay_forecast':['Weather','Weather_d',None],
    # 'Tomorrow_forecast':['Weather','Weather_d',None],
    # 'OfterTomorrow_forecast':['Weather','Weather_d',None],
    # '1Hour_forecast':["1Hour Forecast","Weather",None],
    # '3Hour_forecast':["3Hour_Forecast","Weather",None],
    # '9Hour_forecast':["9Hour_Forecast","Weather",None],
    # '12Hour_forecast':["12Hour_Forecast","Weather",None],
    # '15Hour_forecast':["15Hour_Forecast","Weather",None],
    # '18Hour_forecast':["19Hour_Forecast","Weather",None],
    # '21Hour_forecast':["21Hour_Forecast","Weather",None],
    # 'now':["Now_Forecast","Weather",None],
    # 'suggestion':['Suggestion','comf',None],

}

MODULE_SCHEMA = vol.Schema({
    vol.Required(cv.string, default=[]):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
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
