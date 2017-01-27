"""
Classes to take decisions for transmitting the packets
"""


from threading import Thread
import select

from ..data import Buffer, Msg


class BridgeHandler():
    """Abstract class for bridging policies.
    You just have to subclass and fill the handle method."""

    def __init__(self, coJeu, coSer):
        self.coJeu = coJeu
        self.coSer = coSer
        self.other = {coJeu: coSer, coSer: coJeu}

    def handle(self, data, origin):
        raise NotImplemented


class DummyBridgeHandler(BridgeHandler):
    """Implements a dummy policy
    that transmits all"""

    def handle(self, data, origin):
        other[origin].sendall(data)


class MsgBridgeHandler(BridgeHandler):
    """Advanced policy to work with the parsed messages.
    You just have to subclass and fill the handleMessage method."""

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.buf = {coJeu: Buffer(), coSer: Buffer()}

    def handle(self, data, origin):
        while True:
            self.buf[origin] += data
            msg = Msg.fromRaw(self.buf[origin])
            while msg:
                self.handleMessage(msg, origin)
                msg = Msg.fromRaw(self.buf[origin])

    def handleMessage(self, msg, origin):
        raise NotImplemented


class Bridge(Thread):
    """
    Bridge between the two connections
    that uses a bridge_handler_class
    """

    def __init__(self, coJeu, coSer, bridge_handler_class=DummyBridgeHandler):
        self.conns = [coJeu, coSer]
        self.bridge_handler = bridge_handler_class(coJeu, coSer)
        super().__init__()

    def run(self):
        conns = self.conns
        active = True
        try:
            while active:
                rlist, wlist, xlist = select.select(conns, [], conns)
                if xlist or not rlist:
                    break
                for r in rlist:
                    data = r.recv(8192)
                    if not data:
                        active = False
                        break
                    self.bridge_handler.handle(data, origin=r)
        finally:
            for c in conns:
                c.close()
