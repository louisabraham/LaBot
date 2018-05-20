#!/usr/bin/env python3

from .proxy import startProxyServer
from .proxychains import launchDofus

logger.setLevel('INFO')

# to interrupt : httpd.shutdown()
httpd = startProxyServer()

# you can launch several instances
# of dofus with the same httpd
# the bot will be launched after the connexion
dofus = launchDofus()

