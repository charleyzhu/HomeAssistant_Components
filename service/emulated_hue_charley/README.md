# hue emulated
## Description
Support DingDong Smart SoundBox
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
if you use DingDong Smart SoundBox
Add the following line to the Configuration.yaml.
```
emulated_hue_charley:
    type: dingdong
```

AutoLinkButtn:
Add the following line to the Configuration.yaml.
```
emulated_hue_charley:
    type: dingdong
    auto_link: true
```

Other parameters refer to [HomeAssistant](https://home-assistant.io/components/emulated_hue/)


#中文

# Hue模拟器
## 描述
在原官方模拟器上添加叮咚智能音箱的支持

## 安装
在配置文件目录创建custom_components
复制emulated_hue_charley文件夹到custom_components目录
 ```
 /home/homeassistant/.homeassistant/custom_components
 ```
或者复制到系统目录
 ```
 /srv/homeassistant/homeassistant_venv/lib/python3.4/site-packages/homeassistant/components
 ```

如果是你是使用叮咚智能音箱
在Configuration.yaml文件中添加一下字段
```
emulated_hue_charley:
    type: dingdong
```
自动按下Link按钮
```
emulated_hue_charley:
    type: dingdong
    auto_link: true
```

其他设置参考官方的模拟器设置[emulated_hue](https://home-assistant.io/components/emulated_hue/)

如果模拟器有任何问题请到QQ群或者[论坛](https://bbs.hassbian.com/thread-3135-1-1.html)发布你的问题
