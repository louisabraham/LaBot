"""
Classes to take decisions for transmitting the packets

The classes inheriting from BridgeHandler must
implement `handle`.

The classes inheriting from MsgBridgeHandler must
implement `handle_message`.
"""

import select
from abc import ABC, abstractmethod

from ..data import Buffer, Msg
from .. import protocol


def from_client(origin):
    return origin.getpeername()[0] == "127.0.0.1"


def direction(origin):
    if from_client(origin):
        return "Client->Server"
    else:
        return "Server->Client"


class BridgeHandler(ABC):
    """Abstract class for bridging policies.
    You just have to subclass and fill the handle method.
    
    It implements the proxy_callback that will be called
    when a client tries to connect to the server.
    proxy_callback will call `handle` on every packet.

    To modify the behavior, you have to create subclasses pf
    BridgeHandler.
    """

    def __init__(self, coJeu, coSer):
        self.coJeu = coJeu
        self.coSer = coSer
        self.other = {coJeu: coSer, coSer: coJeu}

    @abstractmethod
    def handle(self, data, origin):
        pass

    @classmethod
    def proxy_callback(cls, coJeu, coSer):
        """Callback that can be called by the proxy

        It creates an instance of the class and
        calls `handle` on every packet

        coJeu: socket to the game
        coSer: socket to the server
        """
        conns = [coJeu, coSer]
        bridge_handler = cls(coJeu, coSer)
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
                    bridge_handler.handle(data, origin=r)
        finally:
            for c in conns:
                c.close()


class DummyBridgeHandler(BridgeHandler):
    """Implements a dummy policy
    that forwards all packets"""

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


class MsgBridgeHandler(DummyBridgeHandler, ABC):
    """
    Advanced policy to work with the parsed messages
    instead of the raw packets like BridgeHandler.
    
    This class implements a generic `handle` that calls 
    `handle_message` which acts on the parsed messages
    and that should be implemented by the subclasses.
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

            self.handle_message(parsedMsg, origin)
            msg = Msg.fromRaw(self.buf[origin], from_client(origin))

    @abstractmethod
    def handle_message(self, msg, origin):
        pass


class PrintingMsgBridgeHandler(MsgBridgeHandler):
    def handle_message(self, msg, origin):
        print(direction(origin))
        print(msg)
        print()
        print()

