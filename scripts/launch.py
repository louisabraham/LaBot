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


parser = argparse.ArgumentParser(
    description="Start the proxy",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)
parser.add_argument("--verbose", default="INFO", help="Logging level")
parser.add_argument(
    "--launch",
    action="store_true",
    help="Launch a proxychained client (only available on macOS)",
)
parser.add_argument(
    "--port", type=int, default=8000, help="Listening port of the proxy server"
)
parser.add_argument(
    "--dump-to", type=Path, default=None, help="Capture file (pickle format)"
)

if __name__ == "__main__":
    args = parser.parse_args()

    logger.setLevel(args.verbose)

    bridges = []

    dumper = Dumper(args.dump_to) if args.dump_to else None

    def my_callback(coJeu, coSer):
        global bridges
        bridge = InjectorBridgeHandler(coJeu, coSer, dumper=dumper)
        bridges.append(bridge)
        bridge.loop()

    # to interrupt : httpd.shutdown()
    httpd = startProxyServer(my_callback, port=args.port)

    # you can launch several instances
    # of dofus with the same httpd
    # the bot will be launched after the connexion
    if args.launch:
        dofus = launchDofus()
