"""
Classes to take decisions for transmitting the packets
"""


from threading import Thread
import select


class BridgeHandler():
    """Implements a bridging policy"""

    def __init__(self, coJeu, coSer):
        self.coJeu = coJeu
        self.coSer = coSer

    def handle(self, data, origin):
        raise NotImplemented


class DummyBridgeHandler(BridgeHandler):
    """Transmits all"""

    def handle(self, data, origin):
        other = self.coJeu if origin is self.coSer else self.coSer
        other.sendall(data)


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
