#!/usr/bin/env python3


import os, sys
# Necessary on macOS if the folder of libdnet is not in
# ctypes.macholib.dyld.DEFAULT_LIBRARY_FALLBACK
# because the newer macOS do not allow to export
# $DYLD_FALLBACK_LIBRARY_PATH with sudo
if os.name == "posix" and sys.platform == "darwin":
    import ctypes.macholib.dyld
    ctypes.macholib.dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, '/opt/local/lib')

import socket
import threading
from select import select
from ..logs import logger

try:
    from scapy3k.all import plist, conf
    from scapy3k.all import Raw, IP
    from scapy3k.data import ETH_P_ALL, MTU
except ImportError:
    from scapy.all import plist, conf
    from scapy.all import Raw, IP, PcapReader
    from scapy.data import ETH_P_ALL, MTU

from ..data import Buffer, Msg


def sniff(store=False, prn=None, lfilter=None,
          stop_event=None, refresh=.1, offline=None, *args, **kwargs):
    """Sniff packets
sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args)
  Modified version of scapy.all.sniff

  store: wether to store sniffed packets or discard them
    prn: function to apply to each packet. If something is returned,
         it is displayed. Ex:
         ex: prn = lambda x: x.summary()
lfilter: python function applied to each packet to determine
         if further action may be done
         ex: lfilter = lambda x: x.haslayer(Padding)
stop_event: Event that stops the function when set
refresh: check stop_event.set() every refresh seconds
    """
    logger.debug("Setting up sniffer...")
    if offline is None:
        L2socket = conf.L2listen
        s = L2socket(type=ETH_P_ALL, *args, **kwargs)
    else:
        s = PcapReader(offline)
    remain = None
    lst = []
    try:
        logger.debug("Started Sniffing")        
        while True:
            if stop_event and stop_event.is_set():
                break
            sel = select([s], [], [], refresh)
            if s in sel[0]:
                p = s.recv(MTU)
                if p is None:
                    break
                if lfilter and not lfilter(p):
                    continue
                if store:
                    lst.append(p)
                if prn:
                    r = prn(p)
                    if r is not None:
                        print(r)
    except KeyboardInterrupt:
        pass
    finally:
        logger.debug("Stopped sniffing.")
        s.close()

    return plist.PacketList(lst, "Sniffed")


def raw(pa):
    """Raw data from a packet
    """
    return bytes(pa.getlayer(Raw))


def from_client(pa):
    logger.debug("Determining packet provenience...")
    dst = pa.getlayer(IP).dst
    src = pa.getlayer(IP).src
    local = socket.gethostbyname(socket.gethostname())
    if src == local:
        logger.debug("Packet comes from local machine")
        return True
    elif dst == local:
        logger.debug("Packet comes from server")
        return False
    assert False


buf1 = Buffer()
buf2 = Buffer()


def on_receive(pa, action):
    """Adds pa to the relevant buffer
    Parse the messages from that buffer
    Calls action on that buffer
    """
    logger.debug("Received packet. ")
    direction = from_client(pa)
    buf = buf1 if direction else buf2
    buf += raw(pa)
    msg = Msg.fromRaw(buf, direction)
    while msg:
        action(msg)
        msg = Msg.fromRaw(buf, direction)


def launch_in_thread(action, capture_file=None):
    """Sniff in a new thread
    When a packet is received, Returns a stop function
    """

    logger.debug("Launching sniffer in thread...")

    def _sniff(stop_event):
        if capture_file:
            sniff(filter='tcp port 5555',
                  lfilter=lambda p: p.haslayer(Raw),
                  stop_event=stop_event,
                  prn=lambda p: on_receive(p, action),
                  offline=capture_file
                  )
        else:
            sniff(filter='tcp port 5555',
                  lfilter=lambda p: p.haslayer(Raw),
                  stop_event=stop_event,
                  prn=lambda p: on_receive(p, action),
                  )
        logger.info('sniffing stopped')

    e = threading.Event()
    t = threading.Thread(target=_sniff, args=(e,))
    t.start()

    def stop():
        e.set()

    logger.debug("Started sniffer in new thread")

    return stop


def on_msg(msg):
    global m
    m = msg
    from pprint import pprint
    pprint(msg.json()['__type__'])
    print(msg.data)
    print(Msg.from_json(msg.json()).data)


if __name__ == '__main__':
    stop = launch_in_thread(on_msg)
