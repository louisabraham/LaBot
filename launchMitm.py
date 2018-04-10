#!/usr/bin/env python3

# from core import protocol
#
# protocol.build()

from core.mitm.proxy import startProxyServer
from core.mitm.proxychains import launchDofus

# to interrupt : httpd.shutdown()
httpd = startProxyServer()

# you can launch several instances
# of dofus with the same httpd
# the bot will be launched after the connexion
dofus = launchDofus()

from core.protocol import *
from core.data import *