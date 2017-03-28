import logging
import voluptuous as vol
from datetime import timedelta
import json

from homeassistant.const import TEMP_CELSIUS ,CONF_LATITUDE, CONF_LONGITUDE,CONF_API_KEY
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
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
CONF_UPDATE_INTERVAL = 'interval'

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
    vol.Required(CONF_AQI,default=[]):vol.All(cv.ensure_list,[vol.In(AQI_TYPES)]),
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
    vol.Optional(CONF_API_KEY): cv.string,
    vol.Optional(CONF_UPDATE_INTERVAL, default=timedelta(seconds=120)): (vol.All(cv.time_period, cv.positive_timedelta)),

})

_Log=logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    api_key = config.get(CONF_API_KEY,None)
    interval = config.get(CONF_UPDATE_INTERVAL)
    monitored_conditions = config[CONF_MONITORED_CONDITIONS]

    if latitude == 0:
        _Log.error('Pls enter latitude!')
        return False

    if longitude == 0:
        _Log.error('Pls enter longitude!')
        return False
    if api_key == None:
        _Log.error('Pls enter api_key!')
        return False

    weatherData = HeWeatherData(
        api_key = api_key,
        latitude = latitude,
        longitude = longitude,
        interval = interval
    )
    weatherData.update()
    if weatherData.data == None:
        _Log.error('weatherData is nil')
        return False

    dev = []
    if  CONF_AQI in monitored_conditions:
        aqiSensor = monitored_conditions['aqi']
        if len(aqiSensor) == 0:
            dev.append(HeWeatherSensor(weatherData, CONF_AQI, 'aqi', 'AQI'))
        for sensor in aqiSensor:
            sensor_Name = AQI_TYPES[sensor][0]
            dev.append(HeWeatherSensor(weatherData,CONF_AQI,sensor,sensor_Name))

    if CONF_TODAY_FORECAST in monitored_conditions:
        DaySensor = monitored_conditions[CONF_TODAY_FORECAST]
        if len(DaySensor) == 0:
            sensor_Name = DAY_FORECAST_TYPES['Weather_d'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_TODAY_FORECAST, 'Weather_d', sensor_Name))
        for sensor in DaySensor:
            sensor_Name = DAY_FORECAST_TYPES[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_TODAY_FORECAST, sensor, sensor_Name))

    if CONF_TOMORROW_FORECAST in monitored_conditions:
        DaySensor = monitored_conditions[CONF_TOMORROW_FORECAST]
        if len(DaySensor) == 0:
            sensor_Name = DAY_FORECAST_TYPES['Weather_d'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_TOMORROW_FORECAST, 'Weather_d',sensor_Name))
        for sensor in DaySensor:
            sensor_Name = DAY_FORECAST_TYPES[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_TOMORROW_FORECAST, sensor, sensor_Name))

    if CONF_OFTERTOMORROW_FORECAST in monitored_conditions:
        DaySensor = monitored_conditions[CONF_OFTERTOMORROW_FORECAST]
        if len(DaySensor) == 0:
            sensor_Name = DAY_FORECAST_TYPES['Weather_d'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_OFTERTOMORROW_FORECAST, 'Weather_d', sensor_Name))
        for sensor in DaySensor:
            sensor_Name = DAY_FORECAST_TYPES[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_OFTERTOMORROW_FORECAST, sensor, sensor_Name))

    if CONF_1HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_1HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_1HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_1HOUR_FORECAST, sensor, sensor_Name))

    if CONF_3HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_3HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_3HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_3HOUR_FORECAST, sensor, sensor_Name))

    if CONF_6HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_6HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_6HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_6HOUR_FORECAST, sensor, sensor_Name))

    if CONF_9HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_9HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_9HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_9HOUR_FORECAST, sensor, sensor_Name))

    if CONF_12HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_12HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_12HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_12HOUR_FORECAST, sensor, sensor_Name))

    if CONF_15HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_15HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_15HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_15HOUR_FORECAST, sensor, sensor_Name))

    if CONF_18HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_18HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_18HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_18HOUR_FORECAST, sensor, sensor_Name))

    if CONF_21HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_21HOUR_FORECAST]
        if len(HourSensor) == 0:
            sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_21HOUR_FORECAST, 'Weather', sensor_Name))
        for sensor in HourSensor:
            sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_21HOUR_FORECAST, sensor, sensor_Name))

    if CONF_NOW in monitored_conditions:
        NowSensor = monitored_conditions[CONF_NOW]
        if len(NowSensor) == 0:
            sensor_Name = NOW_FORECAST_TYPE['Weather'][0]
            dev.append(HeWeatherSensor(weatherData, CONF_NOW, 'Weather', sensor_Name))
        for sensor in NowSensor:
            sensor_Name = NOW_FORECAST_TYPE[sensor][0]
            dev.append(HeWeatherSensor(weatherData, CONF_NOW, sensor, sensor_Name))

    if CONF_SUGGESTION in monitored_conditions:
        SuggestionSensor = monitored_conditions[CONF_SUGGESTION]
        for variable in SuggestionSensor:
            sensors = SuggestionSensor[variable]
            if len(NowSensor) == 0:
                sensor_Name = SUGGESTION_FORECAST_TYPE['brf'][0]
                dev.append(HeWeatherSensor(weatherData, CONF_SUGGESTION, 'brf', sensor_Name))
            for sensor in sensors:
                sensor_Name = SUGGESTION_FORECAST_TYPE[sensor][0]
                dev.append(HeWeatherSensor(weatherData, CONF_SUGGESTION, sensor, sensor_Name))

    add_devices(dev, True)

class HeWeatherSensor(Entity):
    def __init__(self,weatherData,sensor_Type,sensor,sensor_Name):
        """Initialize the sensor."""
        self.weatherData = weatherData
        self._sensor_Type = sensor_Type
        self._name = sensor_Name

        self._state = None

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._sensor_Type == CONF_AQI:
            return self._name
        if self._sensor_Type == CONF_TODAY_FORECAST:
            return 'To'+ self._name
        if self._sensor_Type == CONF_TOMORROW_FORECAST:
            return 'Tomorrow'+ self._name
        if self._sensor_Type == CONF_OFTERTOMORROW_FORECAST:
            return 'OfterTomorrow'+ self._name
        if self._sensor_Type == CONF_1HOUR_FORECAST:
            return '1'+ self._name
        if self._sensor_Type == CONF_3HOUR_FORECAST:
            return '3'+ self._name
        if self._sensor_Type == CONF_6HOUR_FORECAST:
            return '6'+ self._name
        if self._sensor_Type == CONF_9HOUR_FORECAST:
            return '9'+ self._name
        if self._sensor_Type == CONF_12HOUR_FORECAST:
            return '12'+ self._name
        if self._sensor_Type == CONF_15HOUR_FORECAST:
            return '15'+ self._name
        if self._sensor_Type == CONF_18HOUR_FORECAST:
            return '18'+ self._name
        if self._sensor_Type == CONF_21HOUR_FORECAST:
            return '21'+ self._name
        if self._sensor_Type == CONF_NOW:
            return self._name
        if self._sensor_Type == CONF_SUGGESTION:
            return self._name

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

class HeWeatherData(object):
    def __init__(self,api_key,latitude ,longitude,interval):
        self._api_key = api_key
        self.latitude = latitude
        self.longitude = longitude

        self.data = None

        self.update =  Throttle(interval)(self._update)

    def _update(self):
        interface = 'https://free-api.heweather.com/v5/weather?city=%s,%s&key=%s' % (self.longitude,self.latitude,self._api_key)
        resp = requests.get(interface)

        if resp.status_code != 200:
            _Log.error('http get data Error StatusCode:%s' % resp.status_code)
            return

        self.data = resp.json()
        if not 'HeWeather5' in self.data:
            _Log.error('Json Status Error1!')
            return

        HeWeather5 = self.data['HeWeather5']
        HeWeather5Dic = HeWeather5[0]

        if not 'status' in HeWeather5Dic:
            _Log.error('Json Status Error2!')
            return

        status = HeWeather5Dic['status']
        if status != 'ok':
            _Log.error('Json Status Not Good!')
            return
        self.data =HeWeather5Dic