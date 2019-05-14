#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path

# include path to labot
sys.path.append(Path(__file__).absolute().parents[1].as_posix())

from labot.logs import logger
from labot.mitm.proxy import startProxyServer
from labot.mitm.bridge import *

from proxychains import launchDofus


parser = argparse.ArgumentParser(description="Start the proxy")
parser.add_argument("--verbose", default="INFO", help="Logging level")
parser.add_argument(
    "--debug-mitm", action="store_true", help="Prints connexion to the CONNECT proxy"
)
parser.add_argument(
    "--launch",
    action="store_true",
    help="Launch a proxychained client (only available on macOS)",
)
parser.add_argument(
    "--port", type=int, default=8000, help="Listening port of the proxy server"
)

if __name__ == "__main__":
    args = parser.parse_args()

    logger.setLevel(args.verbose)

    bridges = []

    def my_callback(coJeu, coSer):
        global bridges
        bridge = InjectorBridgeHandler(coJeu, coSer)
        bridges.append(bridge)
        bridge.loop()

    # to interrupt : httpd.shutdown()
    httpd = startProxyServer(my_callback, debug=args.debug_mitm, port=args.port)

    # you can launch several instances
    # of dofus with the same httpd
    # the bot will be launched after the connexion
    if args.launch:
        dofus = launchDofus()
