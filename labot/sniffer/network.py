#!/usr/bin/env python3

# Necessary on macOS if the folder of libdnet is not in
# ctypes.macholib.dyld.DEFAULT_LIBRARY_FALLBACK
# because the newer macOS do not allow to export
# $DYLD_FALLBACK_LIBRARY_PATH with sudo
import ctypes.macholib.dyld
ctypes.macholib.dyld.DEFAULT_LIBRARY_FALLBACK.insert(0, '/opt/local/lib')

import socket
import threading
from select import select

try:
    from scapy3k.all import plist, conf
    from scapy3k.all import Raw, IP
    from scapy3k.data import ETH_P_ALL, MTU
except ModuleNotFoundError:
    from scapy.all import plist, conf
    from scapy.all import Raw, IP
    from scapy.data import ETH_P_ALL, MTU

from ..data import Buffer, Msg


def sniff(store=False, prn=None, lfilter=None,
          stop_event=None, refresh=.1, *args, **kwargs):
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
    s = conf.L2listen(type=ETH_P_ALL, *args, **kwargs)
    remain = None
    lst = []
    try:
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
                c += 1
                if prn:
                    r = prn(p)
                    if r is not None:
                        print(r)
    except KeyboardInterrupt:
        pass
    finally:
        s.close()

    return plist.PacketList(lst, "Sniffed")


def raw(pa):
    """Raw data from a packet
    """
    return bytes(pa.getlayer(Raw))


def from_client(pa):
    dst = pa.getlayer(IP).dst
    src = pa.getlayer(IP).src
    local = socket.gethostbyname(socket.gethostname())
    if src == local:
        return True
    elif dst == local:
        return False
    assert False


buf1 = Buffer()
buf2 = Buffer()


def on_receive(pa, action):
    """Adds pa to the relevant buffer
    Parse the messages from that buffer
    Calls action on that buffer
    """
    direction = from_client(pa)
    buf = buf1 if direction else buf2
    buf += raw(pa)
    msg = Msg.fromRaw(buf, direction)
    while msg:
        action(msg)
        msg = Msg.fromRaw(buf, direction)


def launch_in_thread(action):
    """Sniff in a new thread
    When a packet is received, Returns a stop function
    """

    def _sniff(stop_event):
        sniff(filter='tcp port 5555',
              lfilter=lambda p: p.haslayer(Raw),
              stop_event=stop_event,
              prn=lambda p: on_receive(p, action)
              )
        print('sniffing stopped')

    e = threading.Event()
    t = threading.Thread(target=_sniff, args=(e,))
    t.start()

    def stop():
        e.set()

    return stop


def on_msg(msg):
    print(msg)


if __name__ == '__main__':
    launch_in_thread(on_msg)
