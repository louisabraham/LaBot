"""
Classes to take decisions for transmitting the packets

The classes inheriting from BridgeHandler must
implement `handle`.

The classes inheriting from MsgBridgeHandler must
implement `handle_message`.
"""

import select
from abc import ABC, abstractmethod
from collections import deque
import os
import logging
import time

from ..data import Buffer, Msg, Dumper
from .. import protocol

logger = logging.getLogger("labot")
# TODO: use the logger


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
        self.conns = [coJeu, coSer]

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
        bridge_handler = cls(coJeu, coSer)
        bridge_handler.loop()

    def loop(self):
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
                    self.handle(data, origin=r)
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
        from_client = origin == self.coJeu
        # print(direction(origin), self.buf[origin].data)
        msg = Msg.fromRaw(self.buf[origin], from_client)
        while msg is not None:
            msgType = protocol.msg_from_id[msg.id]
            parsedMsg = protocol.read(msgType, msg.data)

            assert msg.data.remaining() == 0, (
                "All content of %s have not been read into %s:\n %s"
                % (msgType, parsedMsg, msg.data)
            )

            self.handle_message(parsedMsg, origin)
            msg = Msg.fromRaw(self.buf[origin], from_client)

    @abstractmethod
    def handle_message(self, msg, origin):
        pass


class PrintingMsgBridgeHandler(MsgBridgeHandler):
    def handle_message(self, msg, origin):
        print(direction(origin))
        print(msg)
        print()
        print()


class InjectorBridgeHandler(BridgeHandler):
    """Forwards all packets and allows to inject
    packets
    """

    def __init__(self, coJeu, coSer, db_size=100, dumper=None):
        super().__init__(coJeu, coSer)
        self.buf = {coJeu: Buffer(), coSer: Buffer()}
        self.injected_to_client = 0
        self.injected_to_server = 0
        self.counter = 0
        self.db = deque([], maxlen=db_size)
        self.dumper = dumper

    def send_to_client(self, data):
        if isinstance(data, Msg):
            data = data.bytes()
        self.injected_to_client += 1
        self.coJeu.sendall(data)

    def send_to_server(self, data):
        if isinstance(data, Msg):
            data.count = self.counter + 1
            data = data.bytes()
        self.injected_to_server += 1
        self.coSer.sendall(data)

    def send_message(self, s):
        msg = Msg.from_json(
            {"__type__": "ChatClientMultiMessage", "content": s, "channel": 0}
        )
        self.send_to_server(msg)

    def handle(self, data, origin):
        self.buf[origin] += data
        from_client = origin == self.coJeu

        msg = Msg.fromRaw(self.buf[origin], from_client)

        while msg is not None:
            msgType = protocol.msg_from_id[msg.id]
            parsedMsg = protocol.read(msgType, msg.data)

            assert msg.data.remaining() in [0, 48], (
                "All content of %s have not been read into %s:\n %s"
                % (msgType, parsedMsg, msg.data)
            )

            if from_client:
                logger.debug(
                    ("-> [%(count)i] %(name)s (%(size)i Bytes)"),
                    dict(
                        count=msg.count,
                        name=protocol.msg_from_id[msg.id]["name"],
                        size=len(msg.data),
                    ),
                )
            else:
                logger.debug(
                    ("<- %(name)s (%(size)i Bytes)"),
                    dict(name=protocol.msg_from_id[msg.id]["name"], size=len(msg.data)),
                )
            if from_client:
                msg.count += self.injected_to_server - self.injected_to_client
                self.counter = msg.count
            else:
                self.counter += 1
            self.db.append(msg)
            if self.dumper is not None:
                self.dumper.dump(msg)
            self.other[origin].sendall(msg.bytes())

            self.handle_message(parsedMsg, origin)
            msg = Msg.fromRaw(self.buf[origin], from_client)

            time.sleep(0.005)

    def handle_message(self, m, o):
        pass
