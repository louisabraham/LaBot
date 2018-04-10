"""
Classes to take decisions for transmitting the packets
"""


from threading import Thread
import select
from pprint import pprint

from ..data import Buffer, Msg
from .. import protocol


def from_client(origin):
    return origin.getpeername()[0] == '127.0.0.1'


def direction(origin):
    if from_client(origin):
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


class PrintingBridgeHandler(DummyBridgeHandler):
    """
    Implements a dummy policy that
    forwards and prints all packets
    """

    def handle(self, data, origin):
        super().handle(data, origin)
        print(direction(origin), data.hex())


class MsgBridgeHandler(DummyBridgeHandler):
    """
    Advanced policy to work with the parsed messages.
    You just have to subclass and fill the handleMessage method
    """

    def __init__(self, coJeu, coSer):
        super().__init__(coJeu, coSer)
        self.buf = {coJeu: Buffer(), coSer: Buffer()}
        
    def handle(self, data, origin):
        
        super().handle(data, origin)
        self.buf[origin] += data        
        
        # print(direction(origin), self.buf[origin].data)
        msg = Msg.fromRaw(self.buf[origin], from_client(origin))
        while msg is not None:
            msgType = protocol.msg_from_id[msg.id]
            parsedMsg = protocol.read(msgType, msg.data)
            
            # TODO: 48 only for messages from client
            assert msg.data.remaining() in [0, 48], (
                "All content of %s have not been read into %s:\n %s"
                % (msgType, parsedMsg, msg.data)
            )
            
            self.handleMessage(parsedMsg, origin)
            msg = Msg.fromRaw(self.buf[origin], from_client(origin))

    def handleMessage(self, msg, origin):
        raise NotImplementedError


class PrintingMsgBridgeHandler(MsgBridgeHandler):

    def handleMessage(self, msg, origin):
        print(direction(origin))
        print(msg)
        print()
        print()


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
