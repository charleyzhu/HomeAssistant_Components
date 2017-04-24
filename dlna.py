"""
Support for Dlna Media Player.

Developed by Charley
"""
import logging
import urllib.parse as urllibparse
import socket
import re
import xml.etree.ElementTree as ET
import requests
from datetime import timedelta

import asyncio

from homeassistant.const import EVENT_HOMEASSISTANT_START
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.core import callback
import homeassistant.util.dt as dt_util
from homeassistant.helpers.discovery import load_platform


DOMAIN = 'dlna'

_LOGGER = logging.getLogger(__name__)

SSDP_BROADCAST_PORT = 1900
SSDP_BROADCAST_ADDR = "239.255.255.250"

SSDP_BROADCAST_PARAMS = ["M-SEARCH * HTTP/1.1",
                         "HOST: {}:{}".format(SSDP_BROADCAST_ADDR,
                                              SSDP_BROADCAST_PORT),
                         "MAN: \"ssdp:discover\"",
                         "MX: 3",
                         "ST: ssdp:all", "", ""]
SSDP_BROADCAST_MSG = "\r\n".join(SSDP_BROADCAST_PARAMS)

UPNP_DEFAULT_SERVICE_TYPE = "urn:schemas-upnp-org:service:AVTransport:1"

SCAN_INTERVAL = timedelta(seconds=15)


@asyncio.coroutine
def async_setup(hass, config):

    dlna = Dlnadriver()
    regDevices = []

    @asyncio.coroutine
    def scan_devices(now):
        """Scan for MediaPlayer."""
        devices = yield from hass.loop.run_in_executor(
            None, dlna.discover_MediaPlayer)



        for device in devices:
            isFind = False
            devUUID = device.get('uuid')

            for regDev in regDevices:
                regUUID = regDev.get('uuid')
                if devUUID == regUUID:
                    isFind = True

            if isFind == False:
                regDevices.append(device)
                load_platform(hass, 'media_player', DOMAIN, device)
                _LOGGER.info('RegDevice:{}'.format(device.get('friendly_name')))
            else:
                isFind = False

            # if device not in regDevices:
            #     regDevices.append(device)
            #     load_platform(hass,'media_player',DOMAIN,device)
            #     _LOGGER.info('RegDevice:{}'.format(device.get('friendly_name')))

            uuid = device.get('uuid')
            if uuid != '':
                hass.data[uuid] = device

        async_track_point_in_utc_time(hass, scan_devices,
                                      dt_util.utcnow() + SCAN_INTERVAL)

    @callback
    def schedule_first(event):
        """Schedule the first discovery when Home Assistant starts up."""
        async_track_point_in_utc_time(hass, scan_devices, dt_util.utcnow())

    hass.bus.async_listen_once(EVENT_HOMEASSISTANT_START, schedule_first)

    return True

class Dlnadriver:

    SOCKET_BUFSIZE = 1024

    def __init__(self):
        self._broadcastsocket = None
        self._listening = None
        self._threads = None

    def register_device(self,location_url):
        try:
            resp = requests.get(location_url,timeout=5)
        except:
            return None

        resp.encoding = 'UTF-8'
        xml = resp.text
        xml = re.sub(" xmlns=\"[^\"]+\"", "", xml, count=1)
        info = ET.fromstring(xml)

        location = urllibparse.urlparse(location_url)
        hostname = location.hostname

        try:
            friendly_name = info.find("./device/friendlyName").text
        except:
            friendly_name = ''

        try:
            uuid = info.find('./device/UDN').text
            if uuid[0:5] == "uuid:":
                uuid = uuid[5:]
        except:
            uuid = ''



        UPNP_DEFAULT_SERVICE_TYPE = re.search("urn:schemas-upnp-org:service:AVTransport:\d+",xml).group()

        try:
            controlURLpath = info.find(
                "./device/serviceList/service/[serviceType='{}']/controlURL".format(
                    UPNP_DEFAULT_SERVICE_TYPE
                )
            ).text
        except:
            controlURLpath = ''

        try:
            SCPDURLpath = info.find(
                "./device/serviceList/service/[serviceType='{}']/SCPDURL".format(
                    UPNP_DEFAULT_SERVICE_TYPE
                )
            )
        except:
            SCPDURLpath = ''


        try:
            eventSubURLpath = info.find(
                "./device/serviceList/service/[serviceType='{}']/eventSubURLpath".format(
                    UPNP_DEFAULT_SERVICE_TYPE
                )
            )
        except:
            eventSubURLpath = ''


        controlURL = urllibparse.urljoin(location_url, controlURLpath)
        SCPDURL = urllibparse.urljoin(location_url, SCPDURLpath)
        eventSubURL = urllibparse.urljoin(location_url, eventSubURLpath)

        device = {
            "location": location_url,
            "hostname": hostname,
            "uuid":uuid,
            "friendly_name": friendly_name,
            "controlURL": controlURL,
            "SCPDURL": SCPDURL,
            "eventSubURL": eventSubURL,
            "st": UPNP_DEFAULT_SERVICE_TYPE
        }

        return device

    def discover_MediaPlayer(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
        s.bind(("", SSDP_BROADCAST_PORT + 20))

        s.sendto(SSDP_BROADCAST_MSG.encode("UTF-8"), (SSDP_BROADCAST_ADDR,
                                                      SSDP_BROADCAST_PORT))

        s.settimeout(5.0)

        devices = []

        while True:

            try:
                data, addr = s.recvfrom(self.SOCKET_BUFSIZE)
                if len(data) is None:
                    continue

            except socket.timeout:
                break

            try:
                info = [a.split(":", 1) for a in data.decode("UTF-8").split("\r\n")[1:]]
                device = dict([(a[0].strip().lower(), a[1].strip()) for a in info if len(a) >= 2])
                devices.append(device)
            except:
                pass

        devices_urls = [device["location"] for device in devices if "AVTransport" in device["st"]]
        devices_urls = list(set(devices_urls))
        devices = []
        for location_url in devices_urls:
            device = self.register_device(location_url)
            if device != None:
                devices.append(device)

        return devices
