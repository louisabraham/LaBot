#!/usr/bin/env python3


"""
This script launches the game through proxychains which
forces every connection to go through the http proxy
"""

import sys
import os.path
import os

from subprocess import PIPE, Popen

from ..logs import logger

confpath = os.path.join(os.path.dirname(__file__), "proxychains.conf")
command = [
    "proxychains4",
    "-f",
    confpath,
    "/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/MacOS/Dofus",
]
newenv = {
    **os.environ,
    "DYLD_INSERT_LIBRARIES": "/System/Library/Frameworks/OpenGL.framework/Resources/GLEngine.bundle/GLEngine",
}


def launchDofus(stdin=PIPE, stdout=PIPE, stderr=PIPE):
    """to interrupt : dofus.terminate()"""
    return Popen(command, env=newenv, stdin=stdin, stdout=stdout, stderr=stderr)


if __name__ == "__main__":
    logger.setLevel("INFO")
    dofus = launchDofus(stdout=sys.stdout, stderr=sys.stderr)
