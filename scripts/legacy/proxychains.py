#!/usr/bin/env python3


"""
This script launches the game through proxychains which
forces every connection to go through the http proxy
"""

import sys
from pathlib import Path

from subprocess import PIPE, Popen


DOFUS_PATH = {
    "darwin": "/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/MacOS/Dofus",
    "linux": None,
    "win32": None,
    "cygwin": None,
}

confpath = Path(__file__).parent / "proxychains.conf"


def launch_dofus(stdin=PIPE, stdout=PIPE, stderr=PIPE):
    """to interrupt : dofus.terminate()"""
    assert sys.platform in DOFUS_PATH, (
        "Your platform (%s) doesn't support proxychains yet" % sys.platform
    )
    command = [
        "proxychains4",
        "-f",
        confpath.absolute().as_posix(),
        DOFUS_PATH[sys.platform],
    ]
    return Popen(command, stdin=stdin, stdout=stdout, stderr=stderr)


if __name__ == "__main__":
    dofus = launch_dofus(stdout=sys.stdout, stderr=sys.stderr)
