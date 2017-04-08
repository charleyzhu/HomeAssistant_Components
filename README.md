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

#### WeatherChina:
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


#### Baidu TTS
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
    person: 1
```

speed,pitch,volume,person is optional 
- speed default=5 value1 0-9
- pitch default=5 value1 0-9
- volume default=5 value1 0-9
- person default=0 value1 0-1
person = 0  = Woman
person = 1  = Man

How get ApiKey and SecretKey? Please register [Baidu developer](http://yuyin.baidu.com)


#### WuKong Remote Control:
Add the following line to the Configuration.yaml.
```
switch:
  - platform: WuKong
    host: 172.16.1.55
    mode:"UDP"
    PrefixName: "XiaoMi"
```
- install [WuKong Remote Control](http://down1.wukongtv.com/yaokong/tv/wkremoteTV-guanwang-release.apk)
- host is Android TV Box Ip Address
- mode is optional 'HTTP:UDP'
- PrefixName is optional

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

####  WeatherChina:
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


#### HeWeather: 和风天气

除了API_KEY以外全是可选字段，API_KEY自己去和风天气[和风天气](https://www.heweather.com)注册

```
 - platform: HeWeather
    api_key: f04c562188764488a86534222cb137bc
    interval: 300
    isShowWeatherPic: True
    city: beihu
    monitored_conditions:
      # 空气质量指数
      aqi:
        # 空气质量指数
        - aqi
        # 一氧化碳
        - co
        # 二氧化氮
        - no2
        # 臭氧
        - o3
        # PM10
        - pm10
        # PM2.5
        - pm25
        # 空气质量
        - qlty
        # 二氧化硫
        - so2
      # 当天预报
      ToDay_forecast:
        # 日出时间
        - sr
        # 日落时间
        - ss
        # 月升时间
        - mr
        # 月落时间
        - ms
        # 白天天气情况
        - Weather_d
        # 夜间天气情况
        - Weather_n
        # 相对湿度
        - hum
        # 降水概率
        - pop
        # 气压
        - pres
        # 最高温度
        - maxTmp
        # 最低温度
        - minTmp
        # 紫外线指数
        - uv
        # 能见度
        - vis
        # 风向（360度）
        - deg
        # 风向
        - dir
        # 风力等级
        - sc
        # 风速
        - spd
      # 明天预报
      Tomorrow_forecast:
        - spd
      # 后天预报
      OfterTomorrow_forecast:
      # 1小时预报
      1Hour_forecast:
        # 天气情况
        - Weather
        # 相对湿度
        - hum
        # 降水概率
        - pop
        # 气压
        - pres
        # 温度
        - tmp
        # 风向（360度）
        - deg
        # 风向
        - dir
        # 风力等级
        - sc
        # 风速
        - spd

      # 3小时预报
      3Hour_forecast:
      # 6小时预报
      6Hour_forecast:
      # 9小时预报
      9Hour_forecast:
      # 12小时预报
      12Hour_forecast:
      # 15小时预报
      15Hour_forecast:
      # 18小时预报
      18Hour_forecast:
      # 21小时预报
      21Hour_forecast:

      # 即时预报
      now:
        # 天气情况
        - Weather
        # 体感温度
        - fl
        # 相对湿度
        - hum
        # 降水量
        - pcpn
        # 气压
        - pres
        # 温度
        - tmp
        # 能见度
        - vis
        # 风向（360度）
        - deg
        # 风向
        - dir
        # 风力等级
        - sc
        # 风速
        - spd
      # 生活指数
      suggestion:
        # 空气指数
        air:
          # 简介
          - brf
          # 数据详情
          - txt
        # 舒适度指数
        comf:
        # 洗车指数
        cw:
        # 穿衣指数
        drsg:
        # 感冒指数
        flu:
        # 运动指数
        sport:
        # 旅游指数
        trav:
        # 紫外线指数
        uv:


```


#### Baidu TTS
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
    person: 1
```
speed,pitch,volume,person 字段为可选值，即可以不写入
- speed 默认=5 取值范围 0-9
- pitch 默认=5 取值范围 0-9
- volume 默认=5 取值范围 0-9
- person 默认=0 取值范围 0-1
person = 0  = 男声
person = 1  = 女声

怎么获取ApiKey和SecretKey? 请注册[百度开发者](http://yuyin.baidu.com)


#### 悟空遥控:
在Configuration.yaml文件中添加一下字段.
```
switch:
  - platform: WuKong
    host: 172.16.1.55
    mode:"UDP"
    PrefixName: "XiaoMi"
```
- 安装 [悟空遥控TV端](http://down1.wukongtv.com/yaokong/tv/wkremoteTV-guanwang-release.apk)
- host: 安装了悟空遥控的安卓盒子(电视)的IP地址
- mode: 是一个可选项 'HTTP:UDP' 如果不输入默认HTTP
- PrefixName: 是一个可选项,用与区分多个设备