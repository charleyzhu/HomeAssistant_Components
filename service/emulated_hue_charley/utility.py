import uuid
import time
import datetime

def get_mac_address():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return ":".join([mac[e:e + 2] for e in range(0, 11, 2)])

def get_mac_address_noformat():
    return uuid.UUID(int=uuid.getnode()).hex[-12:]

def get_bridgeid():
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:]
    return mac[:6] + "fffe" + mac[6:]


def get_local_time():
    return time.strftime('%Y-%m-%dt%H:%M:%S', time.localtime(time.time()))


def get_utc_time():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dt%H:%M:%S")
