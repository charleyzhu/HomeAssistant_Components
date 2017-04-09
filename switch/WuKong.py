"""
Demo platform that has two fake switches.

For more details about this platform, please refer to the documentation
https://home-assistant.io/components/demo/
"""
from homeassistant.components.switch import SwitchDevice
from homeassistant.const import DEVICE_DEFAULT_NAME

from homeassistant.components.switch import PLATFORM_SCHEMA
import homeassistant.helpers.config_validation as cv
from homeassistant.const import CONF_HOST
import voluptuous as vol

import time
import logging
import requests
import socket,base64

DOMAIN = 'Wu_Kong_Control'
CONF_MODE = 'mode'
CONF_PREFIX = 'PrefixName'
_Log=logging.getLogger(__name__)

PACKAGES = {
    'connect'       :'AAC4EwEzAp4AAAgmAAABNAAAAAAAAABEeyJuYW1lIjoiSG9tZSBBc3Npc3RhbnQiLCJjaGFubmVsIjoiaUFwcFN0b3JlIiwiZGV2IjoiaU9TIn0=',
    'tv_ctl_up'     :'AAC4EwEzAp4AAAghAAAAEwAAAAAAAAAA',
    'tv_ctl_down'   :'AAC4EwEzAp4AAAghAAAAFAAAAAAAAAAA',
    'tv_ctl_left'   :'AAC4EwEzAp4AAAghAAAAFQAAAAAAAAAA',
    'tv_ctl_right'  :'AAC4EwEzAp4AAAghAAAAFgAAAAAAAAAA',
    'tv_ctl_home'   :'AAC4EwEzAp4AAAghAAAAAwAAAAAAAAAA',
    'tv_ctl_ok'     :'AAC4EwEzAp4AAAghAAAAFwAAAAAAAAAA',
    'tv_ctl_back'   :'AAC4EwEzAp4AAAghAAAABAAAAAAAAAAA',
    'tv_ctl_volup'  :'AAC4EwEzAp4AAAghAAAAGAAAAAAAAAAA',
    'tv_ctl_voldown':'AAC4EwEzAp4AAAghAAAAGQAAAAAAAAAA',
    'tv_ctl_power'  :'AAC4EwEzAp4AAAghAAAAGgAAAAAAAAAA',
    'tv_ctl_menu'   :'AAC4EwEzAp4AAAghAAAAUgAAAAAAAAAA',
    'tv_ctl_1'      :'AAC4EwEzAp4AAAghAAAACAAAAAAAAAAA',
    'tv_ctl_2'      :'AAC4EwEzAp4AAAghAAAACQAAAAAAAAAA',
    'tv_ctl_3'      :'AAC4EwEzAp4AAAghAAAACgAAAAAAAAAA',
    'tv_ctl_4'      :'AAC4EwEzAp4AAAghAAAACwAAAAAAAAAA',
    'tv_ctl_5'      :'AAC4EwEzAp4AAAghAAAADAAAAAAAAAAA',
    'tv_ctl_6'      :'AAC4EwEzAp4AAAghAAAADQAAAAAAAAAA',
    'tv_ctl_7'      :'AAC4EwEzAp4AAAghAAAADgAAAAAAAAAA',
    'tv_ctl_8'      :'AAC4EwEzAp4AAAghAAAADwAAAAAAAAAA',
    'tv_ctl_9'      :'AAC4EwEzAp4AAAghAAAAEAAAAAAAAAAA',
    'tv_ctl_0'      :'AAC4EwEzAp4AAAghAAAABwAAAAAAAAAA',

}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST,default=None):cv.string,
    vol.Required(CONF_MODE,default='http'):cv.string,
    vol.Required(CONF_PREFIX,default=None):cv.string,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the demo switches."""
    host = config.get(CONF_HOST)
    mode =  config.get(CONF_MODE)
    prefix = config.get(CONF_PREFIX)
    if host == None:
        _Log.error('pls enter host ip address!')
        return False

    # def SendControlCommand(call):
    #     code = call.data.get('code')
    #     _Log.info(code)
    #     hass.states.set('WuKong.Send_Control_Command', code)

    service = WuKongService(hass,host,mode)


    hass.services.register(DOMAIN, 'Send_Control_Command', service.SendControlCommand)
    hass.services.register(DOMAIN, 'Send_Open_Command', service.SendOpenCommand)
    hass.services.register(DOMAIN, 'Send_Install_Command', service.SendInstallCommand)
    hass.services.register(DOMAIN, 'Send_Clean_Command', service.SendCleanCommand)
    hass.services.register(DOMAIN, 'Send_Command_Queue', service.SendCommandQueue)
    hass.services.register(DOMAIN, 'Send_Connect_Command', service.SendConnectCommand)


    add_devices_callback([
        WuKongSwitch(hass, host, prefix, 'tv_ctl_up', False, 'mdi:arrow-up-bold-circle', True, mode,19),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_down', False, 'mdi:arrow-down-bold-circle', True, mode,20),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_left', False, 'mdi:arrow-left-bold-circle', True, mode,21),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_right', False, 'mdi:arrow-right-bold-circle', True, mode,22),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_home', False, 'mdi:home', True, mode,3),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_back', False, 'mdi:backup-restore', True, mode,4),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_ok', False, 'mdi:adjust', True, mode,23),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_volup', False, 'mdi:volume-high', True, mode,24),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_voldown', False, 'mdi:volume-medium', True, mode,25),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_power', False, 'mdi:power', True, mode, 26),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_menu', False, 'mdi:menu', True, mode, 82),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_1', False, 'mdi:numeric-1-box', True, mode,8),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_2', False, 'mdi:numeric-2-box', True, mode,9),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_3', False, 'mdi:numeric-3-box', True, mode,10),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_4', False, 'mdi:numeric-4-box', True, mode,11),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_5', False, 'mdi:numeric-5-box', True, mode,12),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_6', False, 'mdi:numeric-6-box', True, mode,13),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_7', False, 'mdi:numeric-7-box', True, mode,14),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_8', False, 'mdi:numeric-8-box', True, mode,15),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_9', False, 'mdi:numeric-9-box', True, mode,16),
        WuKongSwitch(hass, host, prefix, 'tv_ctl_0', False, 'mdi:numeric-0-box', True, mode,7),

        WuKongSwitch(hass, host, prefix, 'tv_ctl_clean', False, 'mdi:notification-clear-all', True, mode,999),
    ])


class WuKongSwitch(SwitchDevice):
    """Representation of a demo switch."""

    def __init__(self,hass,host,prefix, name, state, icon, assumed,mode,code):
        """Initialize the WuKongSwitch switch."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._state = state
        self._icon = icon
        self._assumed = assumed
        self._code = code
        self._hass = hass
        self._host = host
        self._mode = mode
        self._prefix = prefix

    @property
    def should_poll(self):

        return False

    @property
    def name(self):
        """Return the name of the device if any."""
        if self._prefix != None:
            return self._prefix + '_' + self._name
        return self._name

    @property
    def icon(self):
        """Return the icon to use for device if any."""
        return self._icon

    @property
    def assumed_state(self):
        """Return if the state is based on assumptions."""
        return self._assumed

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self._state

    def turn_on(self, **kwargs):
        """Turn the switch on."""
        self._state = self.sendCode()
        self.schedule_update_ha_state()

    def turn_off(self, **kwargs):
        """Turn the device off."""
        self._state = self.sendCode()
        self.schedule_update_ha_state()

    def sendCode(self):
        s = WuKongService(self._hass, self._host,self._mode)
        if self._code == 999:
            return s.SendCleanCommand(None)
        if self._mode == 'UDP':
            return s.sendUDPPackage(PACKAGES[self._name])
        else:

            return s.SendControlCommand(None,self._code)

class WuKongService(object):

    def __init__(self,hass,host,mode):
        self._host = host
        self._hass = hass
        self._mode = mode

    def SendControlCommand(self,call,selfcode=None):

        if self._mode == 'UDP':
            code = call.data.get('code')
            if code == None:
                _Log.error('Command Code is nil!')
                return
            if code in PACKAGES.keys():
                package = PACKAGES[code]
                return self.sendUDPPackage(package)
            else:
                _Log.error('Code Error!')
                return


        code = ''
        if selfcode == None:
            code = call.data.get('code')
            if code == None:
                _Log.error('Command Code is nil!')
                return
        else:
            code = selfcode
        url = 'http://{host}:8899/send?key={code}'.format(host=self._host, code=code)
        return self.sendHttpRequest(url)

    def SendOpenCommand(self,call,selfappid=None):
        appid = ''
        if selfappid == None:
            appid = call.data.get('appid')
            if appid == None:
                _Log.error('Appid is nil!')
                return
        else:
            appid = selfappid
        url = 'http://{host}:12104/?action=open&pkg={appid}'.format(host=self._host, appid=appid)
        return self.sendHttpRequest(url)

    def SendInstallCommand(self,call,selfappUrl=None):
        appUrl = ''
        if selfappUrl ==None:
            appUrl = call.data.get('appUrl')
            if appUrl == None:
                _Log.error('appUrl is nil!')
                return
        else:
            appUrl = selfappUrl
        url = 'http://{host}:12104/?action=install&url={appUrl}'.format(host=self._host,appUrl=appUrl)
        _Log.error('url:%s' % url)
        return self.sendHttpRequest(url)

    def SendCleanCommand(self,call):
        url = 'http://{host}:12104/?action=clean'.format(host=self._host)
        return self.sendHttpRequest(url)

    def SendConnectCommand(self,call):
        host = call.data.get('host')
        if host == None:
            _Log.error('host is nil!')
            return
        package=PACKAGES["connect"]
        self.sendUDPPackage(package,host)

    def SendCommandQueue(self,call):
        cmdQueue = call.data.get('cmdQueue')
        for cmd in cmdQueue:

            code = cmd.get('code')
            delay = cmd.get('delay')

            if code == None:
                return
            if delay == None:
                delay = 1000
            if self._mode == 'UDP':
                if code in PACKAGES.keys():
                    package = PACKAGES[code]
                    self.sendUDPPackage(package)
                    time.sleep(delay / 1000)
                else:

                    _Log.error('Code Error! code:{cd}'.format(cd=code))
                    return
            else:
                self.SendControlCommand(None,code)
                time.sleep(delay / 1000)

    def sendHttpRequest(self,url):
        url +'&t={time}'.format(time=int(time.time()))
        try:
            resp = requests.get(url)
            if resp.status_code and resp.text == 'success':
                return False
            return True
        except Exception as e:
            _Log.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return False

    def sendUDPPackage(self,base64Data,host=None):
        addr = None
        if host != None:
            addr = (host, 12305)
        else:
            addr = (self._host, 12305)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        bytePackge = base64.b64decode(base64Data)
        ret = True
        try:
            s.sendto(bytePackge,addr)
            ret = False
        except Exception as e:
            _Log.error("requst UDP Error:{err}, Package:{pkg}".format(err=e,pkg=base64Data))
            s.close()

        return ret