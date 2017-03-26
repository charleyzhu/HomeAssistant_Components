# Home Assistan Components by Charley
## Description

This is an Home Assistant components

## Component list

- TTS from Badiu
- sensor from WeatherChina


if you like what you're seeing! give me a smoke,tks. :）

![Donation](https://raw.githubusercontent.com/charleyzhu/HomeAssistant_Components/master/Images/Donation.png)


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

![WeatherChina](https://raw.githubusercontent.com/charleyzhu/HomeAssistant_Components/master/Images/WeatherChina.png)


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

How get ApiKey and SecretKey? Please register [Baidu developer](http://yuyin.baidu.com)

# 中文

# Home Assistant 组件
## 简介
这是本人开发的Home Assistant组件仓库
## 组件列表

- 百度TTS
- 中国天气网传感器

## 如果你感觉这个组件对你有所帮助请赐我根烟 :）

![Donation](https://raw.githubusercontent.com/charleyzhu/HomeAssistant_Components/master/Images/Donation.png)


## 安装方法
在配置文件目录创建custom_components
复制tts、sensor文件夹到custom_components目录
 ```
 /home/homeassistant/.homeassistant/custom_components
 ```
或者复制到系统目录
 ```
 /srv/homeassistant/homeassistant_venv/lib/python3.4/site-packages/homeassistant/components
 ```

 WeatherChina:
在Configuration.yaml文件中添加一下字段
```
sensor:
  - platform: WeatherChina
    CityCode:
    - 101010100
    - 101020100
```
怎么获取CityCode？请打开 [WeatherChina](http://www.weather.com.cn)

按照下图获取CityCode
![WeatherChina](https://raw.githubusercontent.com/charleyzhu/HomeAssistant_Components/master/Images/WeatherChina.png)


Baitu TTS
在Configuration.yaml文件中添加一下字段
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
speed,pitch,volume,peer 字段为可选值，即可以不写入
- speed 默认=5 取值范围 0-9
- pitch 默认=5 取值范围 0-9
- volume 默认=5 取值范围 0-9
- peer 默认=0 取值范围 0-1

怎么获取ApiKey和SecretKey? 请注册[百度开发者](http://yuyin.baidu.com)