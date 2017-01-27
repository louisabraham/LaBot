from com.network.proxy import startProxyServer
from com.network.proxychains import launchDofus

# to interrupt : httpd.shutdown()
httpd = startProxyServer()

# you can launch several instances
# of dofus with the same httpd
# the bot will be launched after the connexion
dofus = launchDofus()