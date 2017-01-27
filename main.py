from network.proxy import startProxyServer
from network.proxychains import launchDofus

# to interrupt : httpd.shutdown()
httpd = startProxyServer()

dofus = launchDofus()