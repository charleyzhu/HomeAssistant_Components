"""
Support for AirPlay.

Developed by Charley
"""

import logging

try:
    from zeroconf import ServiceBrowser, ServiceStateChange, Zeroconf
except ImportError:
    pass

import warnings
import time
import socket
import asyncio
from datetime import timedelta

# from airplay.const import (
#     DOMAIN
# )



from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.const import EVENT_HOMEASSISTANT_START
import homeassistant.util.dt as dt_util
from homeassistant.core import callback
from homeassistant.helpers.discovery import load_platform

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=10)

REQUIREMENTS = ['zeroconf==0.20.0']
DOMAIN = 'airplay'
MEDIA_PLAYER_DOMAIN = 'airplayer'

@asyncio.coroutine
def async_setup(hass, config):
    """Set up the AirPlay component."""
    _LOGGER.debug('Begin setup AirPlay')
    ap = airplay()
    regDevices = []

    @asyncio.coroutine
    def scan_devices(now):
        devices = yield from hass.loop.run_in_executor(
            None, ap.discover_MediaPlayer)

        for device in devices:
            isFind = False

            address = device.get("address")
            port = device.get("port")

            for regDevice in regDevices:
                regAddress = regDevice.get("address")
                regPort = regDevice.get("port")

                if regAddress == address and regPort == port:
                    isFind = True

            if isFind == False:
                regDevices.append(device)
                load_platform(hass, "media_player", MEDIA_PLAYER_DOMAIN, device)
                _LOGGER.debug("find device:%@", device)




        async_track_point_in_utc_time(hass, scan_devices,
                                      dt_util.utcnow() + SCAN_INTERVAL)

    @callback
    def schedule_first(event):
        """Schedule the first discovery when Home Assistant starts up."""
        async_track_point_in_utc_time(hass, scan_devices, dt_util.utcnow())

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, schedule_first)

    return True


class airplay:

    def __init__(self):
        pass

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))

    def discover_MediaPlayer(self, timeout=10, fast=False):
        """
        find airPlay devices
        """

        # this will be our list of devices
        devices = []

        # zeroconf will call this method when a device is found
        def on_service_state_change(zeroconf, service_type, name, state_change):
            if state_change is ServiceStateChange.Added:
                info = zeroconf.get_service_info(service_type, name)
                if info is None:
                    return
                try:
                    name, _ = name.split('.', 1)
                except ValueError:
                    pass

                address = socket.inet_ntoa(info.address)

                devices.append(
                    {
                        "name":name,
                        "address":address,
                        "port":info.port
                    }
                )
            elif state_change is ServiceStateChange.Removed :
                pass

        # search for AirPlay devices
        try:
            zeroconf = Zeroconf()
            browser = ServiceBrowser(zeroconf, "_airplay._tcp.local.", handlers=[on_service_state_change])  # NOQA
        except NameError:
            warnings.warn(
                'AirPlay.find() requires the zeroconf package but it could not be imported. '
                'Install it if you wish to use this method. https://pypi.python.org/pypi/zeroconf',
                stacklevel=2
            )
            return None
        time.sleep(5)
        zeroconf.close()
        return devices
