```
sensor:
  - platform: HeWeather
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
        # 舒适度指数
        air:
          - brf
          - txt
        # 洗车指数
        comf:
        # 穿衣指数
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