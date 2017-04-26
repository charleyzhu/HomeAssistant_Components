"""
Support for Dlna Media Player.

Developed by Charley
"""

import requests
import xml.etree.ElementTree as etree
import re

import homeassistant.util.dt as dt_util
from homeassistant.components.media_player import (
    SUPPORT_NEXT_TRACK, SUPPORT_PAUSE, SUPPORT_PREVIOUS_TRACK, SUPPORT_SEEK,
    SUPPORT_PLAY_MEDIA, SUPPORT_VOLUME_MUTE, SUPPORT_VOLUME_SET, SUPPORT_STOP,
    SUPPORT_TURN_OFF, SUPPORT_PLAY, SUPPORT_VOLUME_STEP, MediaPlayerDevice,
    PLATFORM_SCHEMA, MEDIA_TYPE_MUSIC, MEDIA_TYPE_TVSHOW, MEDIA_TYPE_VIDEO,
    MEDIA_TYPE_PLAYLIST)
from homeassistant.const import (
    STATE_IDLE, STATE_OFF, STATE_PAUSED, STATE_PLAYING)

SUPPORT_DLNA = SUPPORT_PAUSE | SUPPORT_VOLUME_SET | SUPPORT_VOLUME_MUTE | \
    SUPPORT_PREVIOUS_TRACK | SUPPORT_NEXT_TRACK | SUPPORT_VOLUME_STEP |\
    SUPPORT_PLAY_MEDIA | SUPPORT_STOP | SUPPORT_PLAY

import logging

_LOGGER = logging.getLogger(__name__)

SERVER_TYPE_AV = 0
SERVER_TYPE_CONTROL = 1

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the DLNA media player platform."""

    device = DLNADevice(discovery_info.get('location'))
    add_devices([
        DLNAPlayer(hass,device),
    ])

class DLNAPlayer(MediaPlayerDevice):
    """DLNA Device"""

    def __init__(self,hass,device):
        """Initialize DLNA device."""
        self._hass = hass
        self._device = device
        self._name = device.Uuid()
        self._volume = None
        self._muted = None
        self._state = STATE_OFF
        self._media_position_updated_at = None
        self._media_position = None
        self._media_duration = None

    def update(self):
        deviceInfo = self._hass.data[self._device.Uuid()]
        location = deviceInfo.get('location')
        if location != self._device.Location():
            _LOGGER.info ("Device Change!:{}".format(location))
            self._device = DLNADevice(location)




        """Get the latest details from the device."""
        # < allowedValue > STOPPED < / allowedValue >
        # < allowedValue > PAUSED_PLAYBACK < / allowedValue >
        # < allowedValue > PLAYING < / allowedValue >
        # < allowedValue > TRANSITIONING < / allowedValue >
        # < allowedValue > NO_MEDIA_PRESENT < / allowedValue >
        resp = self._device.GetTransportInfo()

        statusCode =  resp.get("status")
        if statusCode != 200:
            self._state = STATE_OFF
            _LOGGER.error("update_state:{}---{}".format(self._device.Uuid(), self._state))
            return True

        respState = resp.get("CurrentTransportState")
        if respState == None:
            self._state = STATE_OFF

        respState = respState.decode('UTF-8')

        if respState == 'STOPPED':
            self._state = STATE_IDLE
        elif respState == 'PAUSED_PLAYBACK':
            self._state = STATE_PAUSED
        elif respState == 'PLAYING':
            self._state = STATE_PLAYING
        elif respState == 'NO_MEDIA_PRESENT':
            self._state = STATE_IDLE
        else:
            pass

        if self._state == STATE_PLAYING:
            positionInfo = self._device.GetPositionInfo()

            statusCode = positionInfo.get("status")
            if statusCode != 200:
                return False

            trackDuration = positionInfo.get('TrackDuration')
            if trackDuration == None:
                return False

            trackDuration = trackDuration.decode('UTF-8')
            trackDurationArr = trackDuration.split(':')
            self._media_duration = (int(trackDurationArr[0]) * 3600 + int(trackDurationArr[1]) * 60 + int(trackDurationArr[2]))


            relTime = positionInfo.get('RelTime')
            if relTime == None:
                return False

            relTime = relTime.decode('UTF-8')
            relTimeArr = relTime.split(':')
            self._media_position = (int(relTimeArr[0]) * 3600 + int(relTimeArr[1]) * 60 + int(relTimeArr[2]) )

            self._media_position_updated_at = dt_util.utcnow()

        mute = self._device.GetMute()
        statusCode = mute.get("status")
        if statusCode == 200:

            currentMute = mute.get("CurrentMute")

            if currentMute != None:
                currentMute = currentMute.decode('UTF-8')
                if currentMute == '0':
                    self._muted = False
                else:
                    self._muted = True


        volume = self._device.GetVolume()
        statusCode = volume.get("status")
        if statusCode == 200:

            currentVolume = volume.get('CurrentVolume')

            if currentVolume != None:
                currentVolumeNum = float(currentVolume) / 100
                self._volume = currentVolumeNum


        return True

    @property
    def name(self):
        """Return the name of the device."""
        return self._name

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def volume_level(self):
        """Volume level of the media player (0..1)."""
        return self._volume

    @property
    def is_volume_muted(self):
        """Boolean if volume is currently muted."""
        return self._muted

    @property
    def supported_features(self):
        """Flag media player features that are supported."""
        return SUPPORT_DLNA

    @property
    def media_content_type(self):
        """Content type of current playing media."""
        return MEDIA_TYPE_MUSIC

    @property
    def media_duration(self):
        """Duration of current playing media in seconds."""
        return self._media_duration

    @property
    def media_position(self):
        """Position of current playing media in seconds."""
        return self._media_position

    @property
    def media_position_updated_at(self):
        """When was the position of the current playing media valid."""
        return self._media_position_updated_at

    def mute_volume(self, mute):

        """Mute the volume."""
        if mute:
            self._device.SetMute(1)
        else:
            self._device.SetMute(0)

        self._muted = mute
        pass

    def set_volume_level(self, volume):
        """Set volume level, range 0..1."""

        vol =  int(float(volume) * 100)
        self._device.SetVolume(vol)
        self._volume = volume
        pass

    def volume_down(self):
        currVolume = int(float(self._volume) * 100)
        currVolume -= 5
        if currVolume < 0:
            currVolume = 0

        self._device.SetVolume(currVolume)
        self._volume = float(currVolume)/100


    def volume_up(self):
        currVolume = int(float(self._volume) * 100)
        currVolume += 5
        if currVolume > 100:
            currVolume = 100

        self._device.SetVolume(currVolume)
        self._volume = float(currVolume)/100


    def media_play(self):
        """Send play commmand."""
        self._device.Play()
        pass

    def media_pause(self):
        """Send pause command."""
        self._device.Pause()
        pass

    def media_stop(self):
        self._device.Stop()

    def media_next_track(self):
        self._device.Next()

    def media_previous_track(self):
        self._device.Previous()

    def play_media(self, media_type, media_id, **kwargs):
        """Send play_media commmand."""
        self._device.SetAVTransportURI(media_id,'')
        self._device.Play()
        pass


class DLNADevice(object):

    def __init__(self,location):
        self.location = location
        resp = requests.get(location)
        resp.encoding = 'utf-8'
        xmlDesc = resp.text

        self.rootDevice = DLNARootDevice(xmlDesc,location)
        self.service = self.rootDevice.Device().Service("urn:upnp-org:serviceId:AVTransport")
        self.control = self.rootDevice.Device().Service("urn:upnp-org:serviceId:RenderingControl")

    def Location(self):
        return self.location

    def Uuid(self):
        return self.rootDevice.Device().Uuid()

    def Name(self):
        return self.rootDevice.Device().FriendlyName()

    def GetCurrentTransportActions(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"GetCurrentTransportActions",fnParams,["Actions"])
        return result

    def GetDeviceCapabilities(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"GetDeviceCapabilities",fnParams,["PlayMedia","RecMedia","RecQualityModes"])
        return result

    def GetMediaInfo(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"GetMediaInfo", fnParams, ["NrTracks", "MediaDuration", "CurrentURI","CurrentURIMetaData",
                                                               "NextURI","NextURIMetaData","PlayMedium","RecordMedium","WriteStatus"])
        return result

    def GetPositionInfo(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"GetPositionInfo",fnParams,["Track","TrackDuration","TrackMetaData","TrackURI","RelTime","AbsTime","RelCount","AbsCount"])
        return result

    def GetTransportInfo(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"GetTransportInfo", fnParams,
                                  ["CurrentTransportState", "CurrentTransportStatus", "CurrentSpeed"])
        return result

    def GetTransportSettings(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"GetTransportSettings", fnParams,["PlayMode", "RecQualityMode"])
        return result

    def Next(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"Next", fnParams,[])
        return result

    def Pause(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"Pause", fnParams, [])
        return result

    def Play(self):
        fnParams = '<InstanceID>0</InstanceID><Speed>1</Speed>'
        result = self.sendRequest(SERVER_TYPE_AV,"Play", fnParams, [])
        return result

    def Stop(self):
        fnParams = '<InstanceID>0</InstanceID><Speed>1</Speed>'
        result = self.sendRequest(SERVER_TYPE_AV,"Stop", fnParams, [])
        return result

    def Previous(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"Previous", fnParams, [])
        return result

    def Seek(self,unit,target):
        # Unit：REL_TIME or TRACK_NR
        # Target： 00: 02:21 TRACK_NR Num
        fnParams = '<InstanceID>0</InstanceID><Unit>{}</Unit><Target>{}</Target>'.format(unit,target)
        result = self.sendRequest(SERVER_TYPE_AV,"Seek", fnParams, [])
        return result

    def SetAVTransportURI(self,uri,metaData):
        fnParams = '<InstanceID>0</InstanceID><CurrentURI>{}</CurrentURI><CurrentURIMetaData>{}</CurrentURIMetaData>'.format(uri,metaData)
        result = self.sendRequest(SERVER_TYPE_AV,"SetAVTransportURI", fnParams, [])
        return result

    def SetNextAVTransportURI(self,uri,metaData):
        fnParams = '<InstanceID>0</InstanceID><NextURI>{}</NextURI><NextURIMetaData>{}</NextURIMetaData>'.format(
            uri, metaData)
        result = self.sendRequest(SERVER_TYPE_AV,"SetNextAVTransportURI", fnParams, [])
        return result

    def SetPlayMode(self,playMode):
        # allowed NewPlayMode = "NORMAL", "REPEAT_ONE", "REPEAT_ALL", "RANDOM"
        fnParams = '<InstanceID>0</InstanceID><NewPlayMode>{}</NewPlayMode>'.format(
            playMode)
        result = self.sendRequest(SERVER_TYPE_AV,"SetPlayMode", fnParams, [])
        return result

    #control

    def GetMute(self):
        fnParams = '<InstanceID>0</InstanceID><Channel>Master</Channel>'
        result = self.sendRequest(SERVER_TYPE_CONTROL, "GetMute", fnParams,["CurrentMute"])
        return result

    def GetVolume(self):
        fnParams = '<InstanceID>0</InstanceID><Channel>Master</Channel>'
        result = self.sendRequest(SERVER_TYPE_CONTROL, "GetVolume", fnParams, ["CurrentVolume"])
        return result

    def ListPresets(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_CONTROL, "ListPresets", fnParams, ["CurrentPresetNameList"])
        return result

    def SelectPreset(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_CONTROL, "SelectPreset", fnParams, ["CurrentPresetNameList"])
        return result

    def SetMute(self,mute):
        fnParams = '<InstanceID>0</InstanceID><Channel>Master</Channel><DesiredMute>{}</DesiredMute>'.format(mute)
        result = self.sendRequest(SERVER_TYPE_CONTROL, "SetMute", fnParams, [])
        return result

    def SetVolume(self,volume):
        fnParams = '<InstanceID>0</InstanceID><Channel>Master</Channel><DesiredVolume>{}</DesiredVolume>'.format(volume)
        result = self.sendRequest(SERVER_TYPE_CONTROL, "SetVolume", fnParams, [])
        return result

    # XiaoMi TV
    def SetRecordQualityMode(self,model):
        fnParams = '<InstanceID>0</InstanceID><NewRecordQualityMode>{}</NewRecordQualityMode>'.format(model)
        result = self.sendRequest(SERVER_TYPE_AV,"SetRecordQualityMode", fnParams, [])
        return result

    def Record(self):
        fnParams = '<InstanceID>0</InstanceID>'
        result = self.sendRequest(SERVER_TYPE_AV,"SetRecordQualityMode", fnParams, [])
        return result


    def sendRequest(self,serverType,fnfunc,fnParams,arguments):
        if serverType == SERVER_TYPE_AV:

            resp = self.soapRequest(self.service.ControlUrl(), self.service.Type(), fnfunc, fnParams)
        else:
            resp = self.soapRequest(self.control.ControlUrl(), self.control.Type(), fnfunc, fnParams)

        if resp == None:
            return {"status": 999,"msg":'send Request Error'}

        result = {
            "status": resp.status_code,
            "msg":'ok'
        }

        respText = resp.text.encode('utf-8')

        respXml = etree.fromstring(respText)

        if resp.status_code != 200:
            try:
                et = respXml[0][0].find("detail/{urn:schemas-upnp-org:control-1-0}UPnPError")
                value = et.find("{urn:schemas-upnp-org:control-1-0}errorDescription").text.encode('utf-8')

            except:
                value = None
            result['msg'] = value

            try:
                et = respXml[0][0].find("detail/{urn:schemas-upnp-org:control-1-0}UPnPError")
                errorcode = et.find("{urn:schemas-upnp-org:control-1-0}errorCode").text.encode('utf-8')
            except:
                errorcode = None
            result['ErrorCode'] = errorcode


        if len(arguments) == 0:

            return result

        for argument in arguments:
            try:
                if serverType == SERVER_TYPE_AV:
                    value = respXml[0].find("{%s}%sResponse/%s" % (self.service.Type(), fnfunc,argument)).text.encode('utf-8')
                else:
                    value = respXml[0].find("{%s}%sResponse/%s" % (self.control.Type(), fnfunc, argument)).text.encode(
                        'utf-8')
            except:
                value = None
            result[argument] = value

        return result

    def soapRequest(self,location, service, fnName, fnParams):
        bodyString = '<?xml version="1.0"?>'
        bodyString += '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
        bodyString += '  <s:Body s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
        bodyString += '    <u:' + fnName + ' xmlns:u="' + service + '">'
        bodyString += '      ' + fnParams
        bodyString += '    </u:' + fnName + '>'
        bodyString += '  </s:Body>'
        bodyString += '</s:Envelope>'

        headers = {
            'Content-Type': 'text/xml',
            'Accept': 'text/xml',
            'SOAPAction': '"'+service + '#' + fnName + '"'
        }
        try:
            res = requests.post(location, data=bodyString, headers=headers,timeout=10)
            res.encoding = 'utf-8'
        except Exception as e:
            _LOGGER.error("send Request Error:{}".format(e))
            return None

        return res


class DLNARootDevice:

    def __init__(self, devDescXml, location):

        self._location = location
        self._urlBase = None
        self._Device = None

        root = etree.fromstring(devDescXml)
        ns = root.tag[1:].split('}')[0]

        # URLBase
        urlBase = root.find('{%s}URLBase' % (ns))
        if urlBase is not None:
            self._urlBase = urlBase.text
        else:
            m = re.match('http://([^/]*)(.*$)', location)
            self._urlBase = 'http://' + m.group(1)

        # Strip off any trailing '/'
        m = re.match('(.*?)(/*$)', self._urlBase)
        if m:
            self._urlBase = m.group(1)

        # create the root device
        device = root.find('{%s}device' % (ns))
        self._Device = DLNAUPNPDevice(device, ns, self)


    def Location(self):
        return self._location

    def SetLocation(self, aLocation):
        self._location = aLocation

    def UrlBase(self):
        return self._urlBase

    def Device(self):
        return self._Device

class DLNAUPNPDevice:

    def __init__(self, devElem, devNs, rootDevice):
        self._RootDevice = rootDevice
        self._ServiceList = []
        self._DeviceList = []

        # deviceType
        try:
            self._Type = devElem.find('{%s}deviceType' % (devNs)).text
        except:
            self._Type = ''

        # UDN
        try:
            self._Uuid = devElem.find('{%s}UDN' % (devNs)).text
            if self._Uuid[0:5] == "uuid:":
                self._Uuid = self._Uuid[5:]
        except:
            self._Uuid = ''

        # friendlyName
        try:
            self._FriendlyName = devElem.find('{%s}friendlyName' % (devNs)).text
        except:
            self._FriendlyName = ''

        # serviceList
        serviceList = devElem.find('{%s}serviceList' % (devNs))
        if serviceList is not None:
            for service in serviceList.getchildren():
                newServ = DLNAService(self, service, devNs)
                self._ServiceList.append(newServ)

        # deviceList
        deviceList = devElem.find('{%s}deviceList' % (devNs))
        if deviceList:
            for device in deviceList.getchildren():
                newDev = DLNAUPNPDevice(device, devNs, rootDevice)
                self._DeviceList.append(newDev)

        # presentationUrl
        try:
            self._PresentationUrl = devElem.find('{%s}presentationURL' % (devNs)).text
        except:
            self._PresentationUrl = ''

    def __str__(self):
        devStr = 'DEVICE:\r\n'
        devStr += 'UUID        : ' + self.Uuid() + '\r\n'
        devStr += 'DEV DESC URL: ' + self.Location() + '\r\n'
        devStr += 'URL BASE    : ' + self.UrlBase() + '\r\n'
        for serv in self._ServiceList:
            devStr += str(serv)
        devStr += '\r\n'
        return devStr

    def Uuid(self):
        return self._Uuid

    def Location(self):
        return self._RootDevice.Location()

    def UrlBase(self):
        return self._RootDevice.UrlBase()

    def Type(self):
        return self._Type

    def FriendlyName(self):
        return self._FriendlyName

    def PresentationUrl(self):
        return self._PresentationUrl

    def SetLocation(self, location):
        self._RootDevice.SetLocation(location)

    def Service(self, servId):
        for serv in self._ServiceList:
            if re.match(servId,serv.Id()):
                return serv
        return None

    def ServiceList(self):
        return self._ServiceList

    def DeviceList(self):
        return self._DeviceList

    def FindDevice(self, uuid):
        if uuid == self._Uuid:
            return self
        for dev in self._DeviceList:
            found = dev.FindDevice(uuid)
            if found != None:
                return found
        return None

class DLNAService:

    def __init__(self, parentDevice, servElem, servNs):
        self._ParentDevice = parentDevice

        self._Type = servElem.find('{%s}serviceType' % (servNs)).text
        self._Id = servElem.find('{%s}serviceId' % (servNs)).text
        self._ScpdUrl = servElem.find('{%s}SCPDURL' % (servNs)).text
        self._ControlUrl = servElem.find('{%s}controlURL' % (servNs)).text

        try:
            self._EventSubUrl = servElem.find('{%s}eventSubURL' % (servNs)).text
        except:
            self._EventSubUrl = None

        self._ActionList = []
        self._StateVarList = []

        # Make sure the relative URLs have a '/' at the front
        if self._ScpdUrl[0:7] != "http://":
            if self._ScpdUrl[0] != '/':
                self._ScpdUrl = self._ParentDevice.UrlBase() + '/' + self._ScpdUrl
            else:
                self._ScpdUrl = self._ParentDevice.UrlBase() + self._ScpdUrl

        if self._ControlUrl[0:7] != "http://":
            if self._ControlUrl[0] != '/':
                self._ControlUrl = self._ParentDevice.UrlBase() + '/' + self._ControlUrl
            else:
                self._ControlUrl = self._ParentDevice.UrlBase() + self._ControlUrl

        if self._EventSubUrl and self._EventSubUrl[0:7] != "http://":
            if self._EventSubUrl[0] != '/':
                self._EventSubUrl = self._ParentDevice.UrlBase() + '/' + self._EventSubUrl
            else:
                self._EventSubUrl = self._ParentDevice.UrlBase() + self._EventSubUrl

        # scpdXml = requests.get(self._ScpdUrl).text.encode('utf-8')
        # self.ParseXmlDesc(scpdXml)



    def __str__(self):
        servStr = '\t' + 'SERVICE:\r\n'
        servStr += '\t' + 'TYPE       : ' + self._Type + '\r\n'
        servStr += '\t' + 'ID         : ' + self._Id + '\r\n'
        servStr += '\t' + 'SCPD URL   : ' + self.ScpdUrl() + '\r\n'
        servStr += '\t' + 'CONTROL URL: ' + self.ControlUrl() + '\r\n'
        if self._EventSubUrl:
            servStr += '\t' + 'EVENT URL  : ' + self.EventSubUrl() + '\r\n'
        return servStr

    def Type(self):
        return self._Type

    def Id(self):
        return self._Id

    def ScpdUrl(self):
        return self._ScpdUrl

    def ControlUrl(self):
        return self._ControlUrl

    def EventSubUrl(self):
        return self._EventSubUrl

    def StateVarList(self):
        return self._StateVarList

    def ActionList(self):
        return self._ActionList

    def ParseXmlDesc(self, xmlDesc):
        "Parse the service description XML file."""

        scpd = etree.fromstring(xmlDesc)
        ns = scpd.tag[1:].split('}')[0]

        # State Variables
        stateVars = scpd.find('{%s}serviceStateTable' % (ns))
        if stateVars is not None:
            for stateVar in stateVars.getchildren():
                name = stateVar.find('{%s}name' % (ns)).text
                type = stateVar.find('{%s}dataType' % (ns)).text
                sendEvs = stateVar.attrib['sendEvents']
                try:
                    default = stateVar.find('{%s}defaultValue' % (ns)).text
                except:
                    default = None

                sv = DLNAService_StateVariable(self, name, type)
                if default:
                    sv.SetDefaultValue(default)

                if sendEvs == 'yes':
                    sv.SetEvented(1)
                else:
                    sv.SetEvented(0)

                allowedVals = stateVar.find('{%s}allowedValueList' % (ns))
                if allowedVals is not None:
                    for allowedVal in allowedVals.getchildren():
                        sv.AddAllowedValue(allowedVal.text)

                allowedValRange = stateVar.find('{%s}allowedValueRange' % (ns))
                if allowedValRange is not None:
                    min = allowedValRange.find('{%s}minimum' % (ns)).text
                    max = allowedValRange.find('{%s}maximum' % (ns)).text
                    try:
                        step = allowedValRange.find('{%s}step' % (ns)).text
                    except:
                        step = '1'
                    sv.SetAllowedValueRange(min, max, step)

                self._StateVarList.append(sv)

        # Actions
        actions = scpd.find('{%s}actionList' % (ns))
        if actions is not None:
            for act in actions.getchildren():
                name = act.find('{%s}name' % (ns)).text
                action = DLNAService_Action(self, name)

                arguments = act.find('{%s}argumentList' % (ns))
                if arguments is not None:
                    for argument in arguments.getchildren():
                        name = argument.find('{%s}name' % (ns)).text
                        dir = argument.find('{%s}direction' % (ns)).text
                        arg = DLNAService_Argument(action, name, dir)

                        rsv = argument.find('{%s}relatedStateVariable' % (ns)).text
                        for sv in self._StateVarList:
                            if rsv == sv.Name():
                                arg.SetRelatedStateVar(sv)
                                break

                self._ActionList.append(action)

class DLNAService_StateVariable:
    """A service state variable."""

    def __init__(self, parent, name, type):
        self._Parent = parent
        self._Name = name
        self._Type = type
        self._DefaultValue = None
        self._AllowedValueList = None
        self._AllowedRangeMin = None
        self._AllowedRangeMax = None
        self._AllowedRangeStep = None
        self._IsEvented = 0

    def SetEvented(self, isEvented):
        self._IsEvented = isEvented

    def SetDefaultValue(self, defVal):
        self._DefaultValue = defVal

    def AddAllowedValue(self, val):
        if self._AllowedValueList == None:
            self._AllowedValueList = []
        self._AllowedValueList.append(val)

    def SetAllowedValueRange(self, min, max, step):
        self._AllowedRangeMin = min
        self._AllowedRangeMax = max
        self._AllowedRangeStep = step

    def IsEvented(self):
        return self._IsEvented

    def Name(self):
        return self._Name

    def Type(self):
        return self._Type

    def DefaultValue(self):
        return self._DefaultValue

    def AllowedValueList(self):
        return self._AllowedValueList

    def AllowedValueRange(self):
        return (self._AllowedRangeMin, self._AllowedRangeMax, self._AllowedRangeStep)

class DLNAService_Action:
    """An action belonging to a service."""

    def __init__(self, parent, name):
        self._Parent  = parent
        self._Name    = name
        self._ArgList = []

    def AddArg(self, arg):
        self._ArgList.append(arg)

    def Name(self):
        return self._Name

    def ArgList(self):
        return self._ArgList

class DLNAService_Argument:
    """An argument of an action."""

    def __init__(self, parent, name, dir):
        self.iParent  = parent
        self.iName    = name
        self.iDir     = dir
        self.iRsv     = None
        self.iParent.AddArg(self)

    def Name(self):
        return self._Name

    def Direction(self):
        return self._Dir

    def RelatedStateVar(self):
        return self._Rsv

    def Type(self):
        if self._Rsv:
            return self._Rsv.Type()
        else:
            return None

    def SetRelatedStateVar(self, rsv):
        self._Rsv = rsv

