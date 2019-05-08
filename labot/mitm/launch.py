#!/usr/bin/env python3

from ..logs import logger
from .proxy import startProxyServer
from .bridge import PrintingMsgBridgeHandler
from .proxychains import launchDofus


logger.setLevel("INFO")

# to interrupt : httpd.shutdown()
httpd = startProxyServer(PrintingMsgBridgeHandler.proxy_callback)

# you can launch several instances
# of dofus with the same httpd
# the bot will be launched after the connexion
dofus = launchDofus()

