#!/usr/bin/env python3

import sys
import os.path
import subprocess


confpath = os.path.join(os.path.dirname(__file__), 'proxychains.conf')
command = ['DYLD_INSERT_LIBRARIES=/System/Library/Frameworks/OpenGL.framework/Resources/GLEngine.bundle/GLEngine',
           'proxychains4', '-f', confpath,
           '/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/MacOS/Dofus']


def launchDofus(stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE):
    """to interrupt : dofus.terminate()"""
    return subprocess.Popen(' '.join(command), shell=True,
                            stdin=stdin, stdout=stdout, stderr=stderr)

if __name__ == '__main__':
    dofus = launchDofus(stderr=sys.stdout)
