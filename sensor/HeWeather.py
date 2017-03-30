import logging
import voluptuous as vol
from datetime import timedelta

from homeassistant.const import TEMP_CELSIUS ,CONF_LATITUDE, CONF_LONGITUDE,CONF_API_KEY
from homeassistant.helpers.entity import Entity
from homeassistant.components.sensor import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.util import Throttle
from homeassistant.const import (
    CONF_MONITORED_CONDITIONS)
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
CONF_CITY = 'city'
CONF_ISSHOWWEATHERPIC = 'isShowWeatherPic'
CONF_ISDEBUG = 'isDebug'

AQI_TYPES = {
    'aqi': ['AQI', None],
    "co": ['AQI_CO', None],
    "no2": ['AQI_NO2', None],
    "o3": ['AQI_O3', None],
    "pm10": ['AQI_PM10', 'mg/m3'],
    "pm25": ['AQI_PM25', 'μg/m3'],
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
    'hum': ['Day_HUM', '%'],
    'pcpn': ['Day_PCPN', 'mm'],
    'pop': ['Day_POP', '%'],
    'pres': ['Day_PRES', None],
    'maxTmp': ['Day_MaxTmp', '°C'],
    'minTmp': ['Day_MinTmp', '°C'],
    'uv': ['Day_UV', None],
    'vis': ['Day_VIS', 'Km'],
    'deg': ['Day_DEG', '°'],
    'dir': ['Day_DIR', None],
    'sc': ['Day_SC', None],
    'spd': ['Day_SPD', 'Km/h'],
}

HOUR_FORECAST_TYPE = {
    'Weather': ['Hour_Weather', None],
    'hum': ['Hour_HUM', None],
    'pop': ['Hour_POP', '%'],
    'pres': ['Hour_PRES', 'hPa'],
    'tmp': ['Hour_Tmp', '°C'],
    'deg': ['Hour_DEG', '°'],
    'dir': ['Hour_DIR', None],
    'sc': ['Hour_SC', None],
    'spd': ['Hour_SPD', 'Km/h'],
}

NOW_FORECAST_TYPE = {
    'Weather': ['Now_Weather', None],
    'fl': ['Now_Fl', None],
    'hum': ['Now_HUM', None],
    'pcpn': ['Now_PCPN', 'mm'],
    'pres': ['Now_PRES', 'hPa'],
    'tmp': ['Now_Tmp', '°C'],
    'vis': ['Now_VIS', 'Km'],
    'deg': ['Now_DEG', '°'],
    'dir': ['Now_DIR', None],
    'sc': ['Now_SC', None],
    'spd': ['Now_SPD', 'Km/h'],
}

Weather_images = {
    '100':'http://www.z4a.net/images/2017/03/29/100.png',
    '101':'http://www.z4a.net/images/2017/03/29/101.png',
    '102':'http://www.z4a.net/images/2017/03/29/102.png',
    '103':'http://www.z4a.net/images/2017/03/29/103.png',
    '104':'http://www.z4a.net/images/2017/03/29/104.png',

    '200':'http://www.z4a.net/images/2017/03/29/200.png',
    '201':'http://www.z4a.net/images/2017/03/29/201.png',
    '202':'http://www.z4a.net/images/2017/03/29/202.png',
    '203':'http://www.z4a.net/images/2017/03/29/202.png',
    '204':'http://www.z4a.net/images/2017/03/29/202.png',
    '205':'http://www.z4a.net/images/2017/03/29/205.png',
    '206':'http://www.z4a.net/images/2017/03/29/205.png',
    '207':'http://www.z4a.net/images/2017/03/29/205.png',
    '208':'http://www.z4a.net/images/2017/03/29/208.png',
    '209':'http://www.z4a.net/images/2017/03/29/208.png',
    '210':'http://www.z4a.net/images/2017/03/29/208.png',
    '211':'http://www.z4a.net/images/2017/03/29/208.png',
    '212':'http://www.z4a.net/images/2017/03/29/208.png',
    '213':'http://www.z4a.net/images/2017/03/29/208.png',

    '300':'http://www.z4a.net/images/2017/03/29/300.png',
    '301':'http://www.z4a.net/images/2017/03/29/301.png',
    '302':'http://www.z4a.net/images/2017/03/29/302.png',
    '303':'http://www.z4a.net/images/2017/03/29/303.png',
    '304':'http://www.z4a.net/images/2017/03/29/304.png',
    '305':'http://www.z4a.net/images/2017/03/29/305.png',
    '306':'http://www.z4a.net/images/2017/03/29/306.png',
    '307':'http://www.z4a.net/images/2017/03/29/307.png',
    '308':'http://www.z4a.net/images/2017/03/29/308.png',
    '309':'http://www.z4a.net/images/2017/03/29/309.png',
    '310':'http://www.z4a.net/images/2017/03/29/310.png',
    '311':'http://www.z4a.net/images/2017/03/29/311.png',
    '312':'http://www.z4a.net/images/2017/03/29/311.png',
    '313':'http://www.z4a.net/images/2017/03/29/313.png',


    '400':'http://www.z4a.net/images/2017/03/29/400.png',
    '401':'http://www.z4a.net/images/2017/03/29/401.png',
    '402':'http://www.z4a.net/images/2017/03/29/402.png',
    '403':'http://www.z4a.net/images/2017/03/29/403.png',
    '404':'http://www.z4a.net/images/2017/03/29/404.png',
    '405':'http://www.z4a.net/images/2017/03/29/405.png',
    '406':'http://www.z4a.net/images/2017/03/29/406.png',
    '407':'http://www.z4a.net/images/2017/03/29/407.png',

    '500':'http://www.z4a.net/images/2017/03/29/500.png',
    '501':'http://www.z4a.net/images/2017/03/29/501.png',
    '502':'http://www.z4a.net/images/2017/03/29/502.png',
    '503':'http://www.z4a.net/images/2017/03/29/503.png',
    '504':'http://www.z4a.net/images/2017/03/29/504.png',
    '505':'http://www.z4a.net/images/2017/03/29/504.png',
    '506':'http://www.z4a.net/images/2017/03/29/504.png',
    '507':'http://www.z4a.net/images/2017/03/29/507.png',
    '508':'http://www.z4a.net/images/2017/03/29/508.png',

    '900':'http://www.z4a.net/images/2017/03/29/900.png',
    '901':'http://www.z4a.net/images/2017/03/29/901.png',
    '999':'http://www.z4a.net/images/2017/03/29/999.png',
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
    vol.Required(CONF_TODAY_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(DAY_FORECAST_TYPES)]),
    vol.Required(CONF_TOMORROW_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(DAY_FORECAST_TYPES)]),
    vol.Required(CONF_OFTERTOMORROW_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(DAY_FORECAST_TYPES)]),
    vol.Required(CONF_1HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_3HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_6HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_9HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_12HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_15HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_18HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_21HOUR_FORECAST,default=None):vol.All(cv.ensure_list, [vol.In(HOUR_FORECAST_TYPE)]),
    vol.Required(CONF_NOW,default=None):vol.All(cv.ensure_list, [vol.In(NOW_FORECAST_TYPE)]),
    vol.Required(CONF_SUGGESTION,default=None): MODULE_SUGGESTION,
})

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_MONITORED_CONDITIONS): MODULE_SCHEMA,
    vol.Optional(CONF_LATITUDE): cv.latitude,
    vol.Optional(CONF_LONGITUDE): cv.longitude,
    vol.Optional(CONF_API_KEY): cv.string,
    vol.Optional(CONF_CITY,default=None):cv.string,
    vol.Optional(CONF_ISSHOWWEATHERPIC,default=False):cv.boolean,
    vol.Optional(CONF_ISDEBUG,default=False):cv.boolean,
    vol.Optional(CONF_UPDATE_INTERVAL, default=timedelta(seconds=120)): (vol.All(cv.time_period, cv.positive_timedelta)),

})

_Log=logging.getLogger(__name__)


def setup_platform(hass, config, add_devices, discovery_info=None):
    latitude = config.get(CONF_LATITUDE, hass.config.latitude)
    longitude = config.get(CONF_LONGITUDE, hass.config.longitude)
    api_key = config.get(CONF_API_KEY,None)
    interval = config.get(CONF_UPDATE_INTERVAL)
    city = config.get(CONF_CITY)
    isShowWeatherPic = config.get(CONF_ISSHOWWEATHERPIC)
    isDebug = config.get(CONF_ISDEBUG)
    monitored_conditions = config[CONF_MONITORED_CONDITIONS]

    if None in (latitude, longitude) and None == city :
        _Log.error("Latitude or longitude or city not set in Home Assistant config")
        return False

    if api_key == None:
        _Log.error('Pls enter api_key!')
        return False

    weatherData = HeWeatherData(
        api_key = api_key,
        latitude = latitude,
        longitude = longitude,
        city = city,
        isDebug= isDebug,
        interval = interval
    )
    weatherData.update()
    weatherData.GetDataBySensor_Type(CONF_AQI)
    if weatherData.data == None:
        _Log.error('weatherData is nil')
        return False

    dev = []
    if  CONF_AQI in monitored_conditions:
        aqiSensor = monitored_conditions['aqi']
        if isinstance(aqiSensor, list):
            if len(aqiSensor) == 0:
                sensor_Name = AQI_TYPES['aqi'][0]
                measurement =  AQI_TYPES['aqi'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_AQI, 'aqi', sensor_Name, isShowWeatherPic,measurement))
            for sensor in aqiSensor:
                sensor_Name = AQI_TYPES[sensor][0]
                measurement = AQI_TYPES[sensor][1]
                dev.append(HeWeatherSensor(weatherData,CONF_AQI,sensor,sensor_Name,measurement))

    if CONF_TODAY_FORECAST in monitored_conditions:
        DaySensor = monitored_conditions[CONF_TODAY_FORECAST]
        if isinstance(DaySensor,list):
            if len(DaySensor) == 0:
                sensor_Name = DAY_FORECAST_TYPES['Weather_d'][0]
                measurement = DAY_FORECAST_TYPES['Weather_d'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_TODAY_FORECAST, 'Weather_d', sensor_Name, isShowWeatherPic,measurement))
            for sensor in DaySensor:
                sensor_Name = DAY_FORECAST_TYPES[sensor][0]
                measurement = DAY_FORECAST_TYPES[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_TODAY_FORECAST, sensor, sensor_Name, isShowWeatherPic,measurement))

    if CONF_TOMORROW_FORECAST in monitored_conditions:
        DaySensor = monitored_conditions[CONF_TOMORROW_FORECAST]
        if isinstance(DaySensor, list):
            if isinstance(DaySensor, list):
                if len(DaySensor) == 0:
                    sensor_Name = DAY_FORECAST_TYPES['Weather_d'][0]
                    measurement = DAY_FORECAST_TYPES['Weather_d'][1]
                    dev.append(HeWeatherSensor(weatherData, CONF_TOMORROW_FORECAST, 'Weather_d',sensor_Name,measurement))
                for sensor in DaySensor:
                    sensor_Name = DAY_FORECAST_TYPES[sensor][0]
                    measurement = DAY_FORECAST_TYPES[sensor][1]
                    dev.append(HeWeatherSensor(weatherData, CONF_TOMORROW_FORECAST, sensor, sensor_Name, isShowWeatherPic,measurement))

    if CONF_OFTERTOMORROW_FORECAST in monitored_conditions:
        DaySensor = monitored_conditions[CONF_OFTERTOMORROW_FORECAST]
        if isinstance(DaySensor, list):
            if len(DaySensor) == 0:
                sensor_Name = DAY_FORECAST_TYPES['Weather_d'][0]
                measurement = DAY_FORECAST_TYPES['Weather_d'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_OFTERTOMORROW_FORECAST, 'Weather_d', sensor_Name, isShowWeatherPic,measurement))
            for sensor in DaySensor:
                sensor_Name = DAY_FORECAST_TYPES[sensor][0]
                measurement = DAY_FORECAST_TYPES[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_OFTERTOMORROW_FORECAST, sensor, sensor_Name, isShowWeatherPic,measurement))

    if CONF_1HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_1HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_1HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic,measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_1HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic,measurement))

    if CONF_3HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_3HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_3HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_3HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_6HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_6HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_6HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_6HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_9HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_9HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_9HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_9HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_12HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_12HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_12HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_12HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_15HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_15HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_15HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_15HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_18HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_18HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_18HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_18HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_21HOUR_FORECAST in monitored_conditions:
        HourSensor = monitored_conditions[CONF_21HOUR_FORECAST]
        if isinstance(HourSensor, list):
            if len(HourSensor) == 0:
                sensor_Name = HOUR_FORECAST_TYPE['Weather'][0]
                measurement = HOUR_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_21HOUR_FORECAST, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in HourSensor:
                sensor_Name = HOUR_FORECAST_TYPE[sensor][0]
                measurement = HOUR_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_21HOUR_FORECAST, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_NOW in monitored_conditions:
        NowSensor = monitored_conditions[CONF_NOW]
        if isinstance(NowSensor, list):
            if len(NowSensor) == 0:
                sensor_Name = NOW_FORECAST_TYPE['Weather'][0]
                measurement = NOW_FORECAST_TYPE['Weather'][1]
                dev.append(HeWeatherSensor(weatherData, CONF_NOW, 'Weather', sensor_Name, isShowWeatherPic, measurement))
            for sensor in NowSensor:
                sensor_Name = NOW_FORECAST_TYPE[sensor][0]
                measurement = NOW_FORECAST_TYPE[sensor][1]
                dev.append(HeWeatherSensor(weatherData, CONF_NOW, sensor, sensor_Name, isShowWeatherPic, measurement))

    if CONF_SUGGESTION in monitored_conditions:
        SuggestionSensor = monitored_conditions[CONF_SUGGESTION]
        if isinstance(SuggestionSensor, dict):
            for variable in SuggestionSensor:
                sensors = SuggestionSensor[variable]
                if len(sensors) == 0:
                    sensor_Name = SUGGESTION_FORECAST_TYPE['brf'][0]
                    measurement = SUGGESTION_FORECAST_TYPE['brf'][1]
                    dev.append(HeWeatherSensor(weatherData, CONF_SUGGESTION, 'brf', sensor_Name, isShowWeatherPic, measurement,variable))
                for sensor in sensors:
                    sensor_Name = SUGGESTION_FORECAST_TYPE[sensor][0]
                    measurement = SUGGESTION_FORECAST_TYPE[sensor][1]
                    dev.append(HeWeatherSensor(weatherData, CONF_SUGGESTION, sensor, sensor_Name, isShowWeatherPic, measurement,variable))

    add_devices(dev, True)

class HeWeatherSensor(Entity):
    def __init__(self,weatherData,sensor_Type,sensor,sensor_Name,isShowWeatherPic,measurement = None,suggestionType = None):
        """Initialize the sensor."""
        self.weatherData = weatherData
        self._sensor_Type = sensor_Type
        self._sensor = sensor
        self._name = sensor_Name
        self._isShowWeatherPic = isShowWeatherPic
        self._unit_of_measurement = measurement
        self._suggestionType = suggestionType

        self._state = None
        self._weatherCode = None

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
            return self._suggestionType + '_'+ self._name

    @property
    def entity_picture(self):
        """Weather symbol if type is symbol."""
        if not self._isShowWeatherPic:
            return
        if self._sensor != 'Weather_d' and self._sensor != 'Weather_n' and self._sensor != 'Weather':
            return None

        if self._weatherCode == None:
            return
        return Weather_images[self._weatherCode]



    @property
    def state(self):
        """Return the state of the sensor."""
        return self._state
    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit_of_measurement

    def update(self):
        self.weatherData.update()
        # _Log.error('_sensor_Type ==%s' % self._sensor)
        if self._sensor_Type == CONF_AQI:
            data = self.weatherData.GetDataBySensor_Type(self._sensor_Type)
            if data == None:
                return
            if 'city' in data:
                cityData = data['city']
                if self._sensor in cityData:
                    statusData = cityData[self._sensor]
                    self._state = statusData

        elif self._sensor_Type == CONF_TODAY_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('daily_forecast')
            if data == None:
                return
            if len(data) > 0 :
                dayData = data[0]
                self._SetDay_Forecast_Status(dayData)
        elif self._sensor_Type == CONF_TOMORROW_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('daily_forecast')
            if data == None:
                return
            if len(data) > 1:
                dayData = data[1]
                self._SetDay_Forecast_Status(dayData)
        elif self._sensor_Type == CONF_OFTERTOMORROW_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('daily_forecast')
            if data == None:
                return
            if len(data) > 2:
                dayData = data[2]
                self._SetDay_Forecast_Status(dayData)

        elif self._sensor_Type == CONF_1HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 0:
                HourData = data[0]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_3HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 2:
                HourData = data[2]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_6HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 3:
                HourData = data[3]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_9HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 4:
                HourData = data[4]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_12HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 5:
                HourData = data[5]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_15HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 6:
                HourData = data[6]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_18HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 7:
                HourData = data[7]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_21HOUR_FORECAST:
            data = self.weatherData.GetDataBySensor_Type('hourly_forecast')
            if data == None:
                return
            if len(data) > 8:
                HourData = data[8]
                self._SetHourly_Forecast_Status(HourData)
        elif self._sensor_Type == CONF_NOW:
            NowData = self.weatherData.GetDataBySensor_Type('now')
            if NowData == None:
                return
            self._SetHourly_Forecast_Status(NowData)
        elif self._sensor_Type == CONF_SUGGESTION:
            suggestionData = self.weatherData.GetDataBySensor_Type('suggestion')
            if suggestionData == None:
                return
            if self._suggestionType == None:
                return

            if self._suggestionType in suggestionData:
                sData = suggestionData[self._suggestionType]
                if self._sensor in sData:
                    statusData = sData[self._sensor]
                    self._state = statusData

    # SetDaily_forecast Data
    def _SetDay_Forecast_Status(self,dayData):

        if self._sensor in ('mr', 'ms', 'sr', 'ss'):
            if 'astro' in dayData:
                astroData = dayData['astro']
                if self._sensor in astroData:
                    statusData = astroData[self._sensor]
                    self._state = statusData

        elif self._sensor in ('Weather_d', 'Weather_n'):
            if 'cond' in dayData:
                condData = dayData['cond']
                sensor = ''
                code = ''
                if self._sensor == 'Weather_d':
                    sensor = 'txt_d'
                    code = 'code_d'
                elif self._sensor == 'Weather_n':
                    sensor = 'txt_n'
                    code = 'code_n'
                if sensor in condData:
                    statusData = condData[sensor]
                    codeData = condData[code]
                    self._state = statusData
                    self._weatherCode = codeData

        elif self._sensor in ('maxTmp', 'minTmp'):
            if 'tmp' in dayData:
                tmpData = dayData['tmp']
                sensor = ''
                if self._sensor == 'maxTmp':
                    sensor = 'max'
                elif self._sensor == 'minTmp':
                    sensor = 'min'

                if sensor in tmpData:
                    statusData = tmpData[sensor]
                    self._state = statusData

        elif self._sensor in ('deg', 'dir', 'sc', 'spd'):
            if 'wind' in dayData:
                windData = dayData['wind']
                if self._sensor in windData:
                    statusData = windData[self._sensor]
                    self._state = statusData

        if self._sensor in dayData:
            statusData = dayData[self._sensor]
            self._state = statusData
    def _SetHourly_Forecast_Status(self,hourlyData):
        if self._sensor == 'Weather':
            if 'cond' in hourlyData:
                condData = hourlyData['cond']
                statusData = condData['txt']
                codeData = condData['code']
                self._state = statusData
                self._weatherCode = codeData

        elif self._sensor in ('deg', 'dir', 'sc', 'spd'):
            if 'wind' in hourlyData:
                windData = hourlyData['wind']
                if self._sensor in windData:
                    statusData = windData[self._sensor]
                    self._state = statusData

        if self._sensor in hourlyData:
            statusData = hourlyData[self._sensor]
            self._state = statusData

class HeWeatherData(object):
    def __init__(self,api_key,latitude ,longitude,city,interval,isDebug):
        self._api_key = api_key
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.isDebug = isDebug

        self.data = None

        self.update =  Throttle(interval)(self._update)


    def _update(self):
        city = '%s,%s' % (self.longitude,self.latitude)

        if not None == self.city:
            city = self.city
        interface = 'https://api.heweather.com/v5/weather?city=%s&key=%s' % (city ,self._api_key)
        
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
        if self.isDebug:
            _Log.info('HeWeather5DicData:%s' % self.data)

    def GetDataBySensor_Type(self,sensor_Type):
        if self.data == None:
            return None
        if sensor_Type in self.data:
            return self.data[sensor_Type]