"""
Classes to take decisions for transmitting the packets
"""


from threading import Thread
import select

from ..data import Buffer, Msg


def direction(origin):
    if origin.getpeername()[0] == '127.0.0.1':
        return 'Client->Server'
    else:
        return 'Server->Client'


class BridgeHandler():
    """Abstract class for bridging policies.
    You just have to subclass and fill the handle method."""

    def __init__(self, coJeu, coSer):
        self.coJeu = coJeu
        self.coSer = coSer
        self.other = {coJeu: coSer, coSer: coJeu}

    def handle(self, data, origin):
        raise NotImplementedError


class DummyBridgeHandler(BridgeHandler):
    """Implements a dummy policy
    that forwards all"""

    def handle(self, data, origin):
        self.other[origin].sendall(data)


class PrintingBridgeHandler(BridgeHandler):
    """Implements a dummy policy
    that forwards and prints all packets"""

    def handle(self, data, origin):
        self.other[origin].sendall(data)
        print(direction(origin), data.hex())


class MsgBridgeHandler(BridgeHandler):
    """Advanced policy to work with the parsed messages.
    You just have to subclass and fill the handleMessage method."""

    def __init__(self, coJeu, coSer):
        super().__init__(coJeu, coSer)
        self.buf = {coJeu: Buffer(), coSer: Buffer()}

    def handle(self, data, origin):
        self.buf[origin] += data
        msg = Msg.fromRaw(self.buf[origin])
        while msg is not None:
            self.handleMessage(msg, origin)
            msg = Msg.fromRaw(self.buf[origin])
                

    def handleMessage(self, msg, origin):
        raise NotImplementedError


class PrintingMsgBridgeHandler(MsgBridgeHandler):

    def handleMessage(self, msg, origin):
        print(direction(origin), msg.id, msg.data.hex())
        self.other[origin].sendall(msg.bytes())

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
