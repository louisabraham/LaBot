#!/usr/bin/env python3


import os
import sys
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
import errno

from scapy.all import plist, conf
from scapy.all import Raw, IP, PcapReader
from scapy.data import ETH_P_ALL, MTU
from scapy.consts import WINDOWS

from ..logs import logger
from ..data import Buffer, Msg


def sniff(store=False, prn=None, lfilter=None,
          stop_event=None, refresh=.1, offline=None, *args, **kwargs):
    """Sniff packets
sniff([count=0,] [prn=None,] [store=1,] [offline=None,] [lfilter=None,] + L2ListenSocket args)
Modified version of scapy.all.sniff

store : bool
    wether to store sniffed packets or discard them

prn : None or callable
    function to apply to each packet. If something is returned,
    it is displayed.
    ex: prn = lambda x: x.summary()

lfilter : None or callable
    function applied to each packet to determine
    if further action may be done
    ex: lfilter = lambda x: x.haslayer(Padding)

stop_event : None or Event
    Event that stops the function when set

refresh : float
    check stop_event.set() every `refresh` seconds
    """
    logger.debug("Setting up sniffer...")
    if offline is None:
        L2socket = conf.L2listen
        s = L2socket(type=ETH_P_ALL, *args, **kwargs)
    else:
        s = PcapReader(offline)

    # on Windows, it is not possible to select a L2socket
    if WINDOWS:
        from scapy.arch.pcapdnet import PcapTimeoutElapsed
        read_allowed_exceptions = (PcapTimeoutElapsed,)

        def _select(sockets):
            return sockets
    else:
        read_allowed_exceptions = ()

        def _select(sockets):
            try:
                return select(sockets, [], [], refresh)[0]
            except select_error as exc:
                # Catch 'Interrupted system call' errors
                if exc[0] == errno.EINTR:
                    return []
                raise
    lst = []
    try:
        logger.debug("Started Sniffing")
        while True:
            if stop_event and stop_event.is_set():
                break
            sel = _select([s])
            if s in sel:
                try:
                    p = s.recv(MTU)
                except read_allowed_exceptions:
                    # could add a sleep(refresh) if the CPU usage
                    # is too much on windows
                    continue
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
    return pa.getlayer(Raw).load


def get_local_ip():
    """from https://stackoverflow.com/a/28950776/5133167
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


LOCAL_IP = get_local_ip()


def from_client(pa):
    logger.debug("Determining packet origin...")
    dst = pa.getlayer(IP).dst
    src = pa.getlayer(IP).src
    if src == LOCAL_IP:
        logger.debug("Packet comes from local machine")
        return True
    elif dst == LOCAL_IP:
        logger.debug("Packet comes from server")
        return False
    logger.error("Packet origin unknown\nsrc: %s\ndst: %s\nLOCAL_IP: %s",
                 src, dst, LOCAL_IP)
    assert False, "Packet origin unknown"


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
    When a packet is received, calls action
    Returns a stop function
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
