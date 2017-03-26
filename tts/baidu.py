"""
Baidu TTS　Developer by Charley
"""
import voluptuous as vol
from homeassistant.components.tts import Provider, PLATFORM_SCHEMA, CONF_LANG
import homeassistant.helpers.config_validation as cv

import requests
import logging
import json

_Log=logging.getLogger(__name__)

# 默认语言
DEFAULT_LANG = 'zh'

# 支持的语言
SUPPORT_LANGUAGES = [
    'zh',
]

CONF_APIKEY = 'api_key'
CONF_SECRETKEY = 'secret_key'
CONF_SPEED =  'speed'
CONF_PITCH = 'pitch'
CONF_VOLUME = 'volume'
PERSON = 'person'


TOKEN_INTERFACE = 'https://openapi.baidu.com/oauth/2.0/token'
TEXT2AUDIO_INTERFACE = 'http://tsn.baidu.com/text2audio'

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Optional(CONF_LANG, default=DEFAULT_LANG): vol.In(SUPPORT_LANGUAGES),
    vol.Optional(CONF_APIKEY): cv.string,
    vol.Optional(CONF_SECRETKEY):cv.string,
    vol.Optional(CONF_SPEED,default='5'): cv.string,
    vol.Optional(CONF_PITCH,default='5'): cv.string,
    vol.Optional(CONF_VOLUME,default='5'): cv.string,
    vol.Optional(PERSON,default='0'): cv.string,
})

def get_engine(hass, config):
    lang = config.get(CONF_LANG)
    apiKey = config.get(CONF_APIKEY)
    secretKey = config.get(CONF_SECRETKEY)
    speed = config.get(CONF_SPEED)
    pitch = config.get(CONF_PITCH)
    volume = config.get(CONF_VOLUME)
    person = config.get(PERSON)

    if apiKey == None:
        _Log.error('Api Key is nil')
        return False
    if secretKey == None:
        _Log.error('secretKey is nil')
        return False

    return BaiduTTS(lang,apiKey,secretKey,speed,pitch,volume,person)

class BaiduTTS (Provider):

    def __init__(self,lang,apiKey,secretKey,speed,pitch,volume,person):
        self._lang = lang
        self._apiKey = apiKey
        self._secretKey = secretKey
        self._speed = speed
        self._pitch = pitch
        self._volume = volume
        self._person = person
        token = self.getToken()
        _Log.info("token =====>" + token)
        self._Token = token

    def getToken(self):
        resp = requests.get(TOKEN_INTERFACE,params={'grant_type': 'client_credentials','client_id':self._apiKey,'client_secret':self._secretKey})
        if resp.status_code != 200:
            _Log.error('Get ToKen Http Error status_code:%s' % resp.status_code)
            return None
        resp.encoding = 'utf-8'
        # toKenjsonStr =  resp.text
        tokenJson =  resp.json()

        if not 'access_token' in tokenJson:
            _Log.error('Get ToKen Json Error!')
            return None
        return tokenJson['access_token']

    @property
    def default_language(self):
        """Default language."""
        return self._lang

    @property
    def supported_languages(self):
        """List of supported languages."""
        return SUPPORT_LANGUAGES

    def get_tts_audio(self, message, language, options=None):
        if self._Token == None:
            self._Token = self.getToken()

        if self._Token == None:
            _Log.error('get_tts_audio Self.ToKen is nil')
            return

        resp = requests.get(TEXT2AUDIO_INTERFACE,params={'tex':message,'lan':language,'tok':self._Token,'ctp':'1','cuid':'HomeAssistant','spd':self._speed,'pit':self._pitch,'vol':self._volume,'per':self._person})

        if resp.status_code == 500:
            _Log.error('Text2Audio Error:500 Not Support.')
            return
        if resp.status_code == 501:
            _Log.error('Text2Audio Error:501 Params Error')
            return
        if resp.status_code == 502:
            _Log.error('Text2Audio Error:502 TokenVerificationError.')
            _Log.Info('Now Get Token!')
            self._Token = self.getToken()
            self.get_tts_audio(message,language,options)
            return
        if resp.status_code == 503:
            _Log.error('Text2Audio Error:503 Composite Error.')
            return

        if resp.status_code != 200:
            _Log.error('get_tts_audio Http Error status_code:%s' % resp.status_code)
            return

        data = resp.content
        return ('mp3',data)