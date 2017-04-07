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
from homeassistant.core import ServiceCall
import voluptuous as vol

import time
import logging
import requests

DOMAIN = 'Wu_Kong_Control'
_Log=logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_HOST,default=None):cv.string,
})

# pylint: disable=unused-argument
def setup_platform(hass, config, add_devices_callback, discovery_info=None):
    """Setup the demo switches."""
    host = config.get(CONF_HOST)
    if host == None:
        _Log.error('pls enter host ip address!')
        return False

    # def SendControlCommand(call):
    #     code = call.data.get('code')
    #     _Log.info(code)
    #     hass.states.set('WuKong.Send_Control_Command', code)

    service = WuKongService(hass,host)


    hass.services.register(DOMAIN, 'Send_Control_Command', service.SendControlCommand)
    hass.services.register(DOMAIN, 'Send_Open_Command', service.SendOpenCommand)
    hass.services.register(DOMAIN, 'Send_Install_Command', service.SendInstallCommand)
    hass.services.register(DOMAIN, 'Send_Clean_Command', service.SendCleanCommand)
    hass.services.register(DOMAIN, 'Send_Command_Queue', service.SendCommandQueue)


    add_devices_callback([
        WuKongSwitch(hass, host, 'tv_ctl_up', False, 'mdi:arrow-up-bold-circle', True,19),
        WuKongSwitch(hass, host, 'tv_ctl_down', False, 'mdi:arrow-down-bold-circle', True,20),
        WuKongSwitch(hass, host, 'tv_ctl_left', False, 'mdi:arrow-left-bold-circle', True,21),
        WuKongSwitch(hass, host, 'tv_ctl_right', False, 'mdi:arrow-right-bold-circle', True,22),
        WuKongSwitch(hass, host, 'tv_ctl_home', False, 'mdi:home', True,3),
        WuKongSwitch(hass, host, 'tv_ctl_back', False, 'mdi:backup-restore', True,4),
        WuKongSwitch(hass, host, 'tv_ctl_ok', False, 'mdi:adjust', True,23),
        WuKongSwitch(hass, host, 'tv_ctl_volup', False, 'mdi:volume-high', True,24),
        WuKongSwitch(hass, host, 'tv_ctl_voldown', False, 'mdi:volume-medium', True,25),
        WuKongSwitch(hass, host, 'tv_ctl_power', False, 'mdi:power', True, 26),
        WuKongSwitch(hass, host, 'tv_ctl_menu', False, 'mdi:menu', True, 82),
        WuKongSwitch(hass, host, 'tv_ctl_1', False, 'mdi:numeric-1-box', True,8),
        WuKongSwitch(hass, host, 'tv_ctl_2', False, 'mdi:numeric-2-box', True,9),
        WuKongSwitch(hass, host, 'tv_ctl_3', False, 'mdi:numeric-3-box', True,10),
        WuKongSwitch(hass, host, 'tv_ctl_4', False, 'mdi:numeric-4-box', True,11),
        WuKongSwitch(hass, host, 'tv_ctl_5', False, 'mdi:numeric-5-box', True,12),
        WuKongSwitch(hass, host, 'tv_ctl_6', False, 'mdi:numeric-6-box', True,13),
        WuKongSwitch(hass, host, 'tv_ctl_7', False, 'mdi:numeric-7-box', True,14),
        WuKongSwitch(hass, host, 'tv_ctl_8', False, 'mdi:numeric-8-box', True,15),
        WuKongSwitch(hass, host, 'tv_ctl_9', False, 'mdi:numeric-9-box', True,16),
        WuKongSwitch(hass, host, 'tv_ctl_0', False, 'mdi:numeric-0-box', True,7),

        WuKongSwitch(hass, host, 'tv_ctl_clean', False, 'mdi:notification-clear-all', True,999),
    ])


class WuKongSwitch(SwitchDevice):
    """Representation of a demo switch."""

    def __init__(self,hass,host, name, state, icon, assumed,code):
        """Initialize the WuKongSwitch switch."""
        self._name = name or DEVICE_DEFAULT_NAME
        self._state = state
        self._icon = icon
        self._assumed = assumed
        self._code = code
        self._hass = hass
        self._host = host

    @property
    def should_poll(self):

        return False

    @property
    def name(self):
        """Return the name of the device if any."""
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
        s = WuKongService(self._hass,self._host)
        if self._code == 999:
            return s.SendCleanCommand(None)
        return s.SendControlCommand(None,self._code)

class WuKongService(object):

    def __init__(self,hass,host):
        self._host = host
        self._hass = hass

    def SendControlCommand(self,call,selfcode=None):
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
        return self.sendHttpRequest(url)

    def SendCleanCommand(self,call):
        url = 'http://{host}:12104/?action=clean'.format(host=self._host)
        return self.sendHttpRequest(url)

    def SendCommandQueue(self,call):
        cmdQueue = call.data.get('cmdQueue')
        for cmd in cmdQueue:
            code = cmd.get('code')
            delay = cmd.get('delay')
            if code == None:
                return
            if delay == None:
                delay = 1000
            self.SendControlCommand(None,code)
            time.sleep(delay / 1000)

    def sendHttpRequest(self,url):
        url +'&t={time}'.format(time=int(time.time()))
        try:
            resp = requests.get(url)
            if resp.status_code and resp.text == 'success':
                return True
            return False
        except Exception as e:
            _Log.error("requst url:{url} Error:{err}".format(url=url,err=e))
            return False