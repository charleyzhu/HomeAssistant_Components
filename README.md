# Home Assistan Components by Charley
## Description

This is an Home Assistant components

## Component list

- TTS from Badiu
- sensor from WeatherChina


if you like what you're seeing! give me a smoke,tks.

![alt tag](https://raw.githubusercontent.com/charleyzhu/HomeAssistant_Components/master/Donation.png)


## Installation
------
copy all the files into the Home Assistant location. It can now be installed either to the custom_components folder 
 ```
 /home/homeassistant/.homeassistant/custom_components
 ```
 or the root folder (using virtual environment)
 ```
 /srv/homeassistant/homeassistant_venv/lib/python3.4/site-packages/homeassistant/components
 ```

One Gateway

WeatherChina:
Add the following line to the Configuration.yaml.
```
sensor:
  - platform: WeatherChina
    CityCode:
    - 101010100
    - 101020100
```

How get zhe citycode ,pls open [WeatherChina](http://www.weather.com.cn)

![alt tag](https://raw.githubusercontent.com/charleyzhu/HomeAssistant_Components/master/Donation.png)


Baitu TTS
Add the following line to the Configuration.yaml.
```
tts:
  - platform: baidu
    language: zh
    api_key: 12345678
    secret_key: 87654321
    speed: 5
    pitch: 5
    volume: 5
    peer: 1
```

speed,pitch,volume,peer is optional 
- speed default=5 value1 0-9
- pitch default=5 value1 0-9
- volume default=5 value1 0-9
- peer default=0 value1 0-1


How get ApiKey and SecretKey? Please register Baidu developer