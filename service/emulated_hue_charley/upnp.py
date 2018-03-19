"""Provides a UPNP discovery method that mimics Hue hubs."""
import threading
import socket
import logging
import select

from aiohttp import web

from homeassistant import core
from homeassistant.components.http import HomeAssistantView
from .utility import *

_LOGGER = logging.getLogger(__name__)


class DescriptionXmlView(HomeAssistantView):
    """Handles requests for the description.xml file."""

    url = '/description.xml'
    name = 'description:xml'
    requires_auth = False

    def __init__(self, config):
        """Initialize the instance of the view."""
        self.config = config

    @core.callback
    def get(self, request):
        """Handle a GET request."""
        xml_template = """<?xml version="1.0" encoding="UTF-8" ?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
<specVersion>
<major>1</major>
<minor>0</minor>
</specVersion>
<URLBase>http://{0}:{1}/</URLBase>
<device>
<deviceType>urn:schemas-upnp-org:device:Basic:1</deviceType>
<friendlyName>HASS Bridge ({0})</friendlyName>
<manufacturer>Royal Philips Electronics</manufacturer>
<manufacturerURL>http://www.philips.com</manufacturerURL>
<modelDescription>Philips hue Personal Wireless Lighting</modelDescription>
<modelName>Philips hue bridge 2015</modelName>
<modelNumber>BSB002</modelNumber>
<modelURL>http://www.meethue.com</modelURL>
<serialNumber>{2}</serialNumber>
<UDN>uuid:01234567-89ab-cdef-0123-{2}</UDN>
</device>
</root>
"""

        resp_text = xml_template.format(
            self.config.advertise_ip, self.config.advertise_port,get_mac_address_noformat())

        return web.Response(text=resp_text, content_type='text/xml')


class UPNPResponderThread(threading.Thread):
    """Handle responding to UPNP/SSDP discovery requests."""

    _interrupted = False

    def __init__(self, host_ip_addr, listen_port, upnp_bind_multicast,
                 advertise_ip, advertise_port):
        """Initialize the class."""
        threading.Thread.__init__(self)

        self.host_ip_addr = host_ip_addr
        self.listen_port = listen_port
        self.upnp_bind_multicast = upnp_bind_multicast

        # Note that the double newline at the end of
        # this string is required per the SSDP spec
        resp_template = """HTTP/1.1 200 OK
CACHE-CONTROL: max-age=60
EXT:
LOCATION: http://{0}:{1}/description.xml
SERVER: HomeAssistant/0.6.5, UPnP/1.0, IpBridge/0.1
hue-bridgeid: {2}
ST: upnp:rootdevice
USN: uuid:01234567-89ab-cdef-0123-{3}::upnp:rootdevice

"""

        self.upnp_response = resp_template.format(
            advertise_ip, advertise_port, get_bridgeid(),get_mac_address_noformat()).replace("\n", "\r\n") \
                                         .encode('utf-8')

    def run(self):
        """Run the server."""
        # Listen for UDP port 1900 packets sent to SSDP multicast address
        ssdp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ssdp_socket.setblocking(False)

        # Required for receiving multicast
        ssdp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        ssdp_socket.setsockopt(
            socket.SOL_IP,
            socket.IP_MULTICAST_IF,
            socket.inet_aton(self.host_ip_addr))

        ssdp_socket.setsockopt(
            socket.SOL_IP,
            socket.IP_ADD_MEMBERSHIP,
            socket.inet_aton("239.255.255.250") +
            socket.inet_aton(self.host_ip_addr))

        if self.upnp_bind_multicast:
            ssdp_socket.bind(("", 1900))
        else:
            ssdp_socket.bind((self.host_ip_addr, 1900))

        while True:
            if self._interrupted:
                clean_socket_close(ssdp_socket)
                return

            try:
                read, _, _ = select.select(
                    [ssdp_socket], [],
                    [ssdp_socket], 2)

                if ssdp_socket in read:
                    data, addr = ssdp_socket.recvfrom(1024)
                else:
                    # most likely the timeout, so check for interrupt
                    continue
            except socket.error as ex:
                if self._interrupted:
                    clean_socket_close(ssdp_socket)
                    return

                _LOGGER.error("UPNP Responder socket exception occurred: %s",
                              ex.__str__)
                # without the following continue, a second exception occurs
                # because the data object has not been initialized
                continue

            if "M-SEARCH" in data.decode('utf-8', errors='ignore'):
                # SSDP M-SEARCH method received, respond to it with our info
                resp_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_DGRAM)

                resp_socket.sendto(self.upnp_response, addr)
                resp_socket.close()

    def stop(self):
        """Stop the server."""
        # Request for server
        self._interrupted = True
        self.join()


def clean_socket_close(sock):
    """Close a socket connection and logs its closure."""
    _LOGGER.info("UPNP responder shutting down.")

    sock.close()
