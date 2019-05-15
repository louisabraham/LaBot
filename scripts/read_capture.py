#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
import pickle
from collections import deque
import logging

logger = logging.getLogger("labot")

# include path to labot
sys.path.append(Path(__file__).absolute().parents[1].as_posix())

from labot import protocol
from labot.data import Msg

parser = argparse.ArgumentParser(
    description="try to read all packets in a capture file produced by `launch_mitm.py --dump-to capture.pk`"
)

parser.add_argument("file", type=Path, help="Capture file (pickle format)")
parser.add_argument(
    "--keep",
    type=int,
    default=100,
    help="number of packets to keep in memory (might use a lot of RAM)",
)
parser.add_argument("--verbose", default="INFO", help="Logging level")


# TODO: add dump of output

if __name__ == "__main__":
    args = parser.parse_args()
    logger.setLevel(args.verbose)

    db = deque([], maxlen=args.keep)
    with args.file.open("rb") as f:
        while True:
            try:
                msg: Msg = pickle.load(f)
                db.append(msg)
                msg.json()
                logger.info("Successfully read %s", msg.msgType["name"])
                assert msg.data.remaining() == 0
            except EOFError:
                break
            except Exception:
                logger.setLevel("DEBUG")
                msg.data.reset()
                msg.json()

