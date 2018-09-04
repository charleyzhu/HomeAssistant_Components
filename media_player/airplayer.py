"""
Support for AirPlay.

Developed by Charley
"""

import requests

import homeassistant.util.dt as dt_util
from homeassistant.components.media_player import (
    SUPPORT_NEXT_TRACK, SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK, SUPPORT_SEEK,
    SUPPORT_PLAY_MEDIA, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_STOP,
    SUPPORT_TURN_OFF, SUPPORT_PLAY, SUPPORT_VOLUME_STEP, MediaPlayerDevice,
    PLATFORM_SCHEMA, MEDIA_TYPE_MUSIC, MEDIA_TYPE_VIDEO,MEDIA_TYPE_URL,
    MEDIA_TYPE_PLAYLIST)
from homeassistant.const import (
    STATE_IDLE, STATE_OFF, STATE_PAUSED, STATE_PLAYING)

SUPPORT_AIRPLAY = SUPPORT_PLAY_MEDIA

import logging

_LOGGER = logging.getLogger(__name__)

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the AirPlay media player platform."""
    if discovery_info is not None:

        add_devices([
            air_player(
                hass,
                discovery_info.get('name'),
                discovery_info.get('address'),
                discovery_info.get('port'),
            ),
        ])

class air_player(MediaPlayerDevice):
    """AirPlay Device"""

    def __init__(self,hass,name,address,port):
        """Initialize AirPlay device."""
        self._hass = hass
        self._deviceUrl = "http://%s:%s" % (address, port)
        self._name = name
        self._address = address
        self._port = port

        self._state = STATE_OFF

    def update(self):
        infoResp = self.getDeviceInfo()
        if infoResp == None:
            self._state = STATE_OFF
            return
        else:
            if infoResp.status_code != 200:
                self._state = STATE_OFF
                return
            self._state = STATE_IDLE

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        return self._state

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_AIRPLAY

    def media_play(self):
        """Send play commmand."""
        pass

    def play_media(self, media_type, media_id, **kwargs):
        """Send play_media commmand."""
        self.play(media_id)

    def getDeviceInfo(self):
        return self.getData("/server-info")

    def getPlayback_info(self):
        return self.getData("/playback-info")

    def play(self,url):
        data = """Content-Location: %s
        Start-Position: 0""" % (url)

        self.postData("/play",data=data)

    def getData(self,path):
        try:
            resp = requests.get("%s%s" % (self._deviceUrl,path),timeout=2)
            resp.encoding = 'utf-8'
        except Exception as e:
            return None
        return resp

    def postData(self,path,data=None,header=None):
        try:
            # proxies = {
            #             #     'http': 'http://127.0.0.1:8082',
            #             #     'https': 'http://127.0.0.1:8082',
            #             # }
            resp = requests.post("%s%s" % (self._deviceUrl,path),data=data,headers=header,timeout=2)
            resp.encoding = 'utf-8'
        except Exception as e:
            return None
        return resp
