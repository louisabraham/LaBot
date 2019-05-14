#!/usr/bin/env python3

from ..logs import logger
from .proxy import startProxyServer
from .bridge import *
from .proxychains import launchDofus


logger.setLevel("INFO")

# to interrupt : httpd.shutdown()
bridges = []


def my_callback(coJeu, coSer):
    global bridges
    bridge = InjectorBridgeHandler(coJeu, coSer)
    bridges.append(bridge)
    bridge.loop()


httpd = startProxyServer(my_callback, debug=True)

# TODO: option to launch

# you can launch several instances
# of dofus with the same httpd
# the bot will be launched after the connexion
dofus = launchDofus()

