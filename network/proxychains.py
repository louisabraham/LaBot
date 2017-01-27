#!/usr/bin/env python3

import os.path
import subprocess


confpath = os.path.join(os.path.dirname(__file__), 'config.json')
command = ['DYLD_INSERT_LIBRARIES=/System/Library/Frameworks/OpenGL.framework/Resources/GLEngine.bundle/GLEngine',
           'proxychains4',
           '-f', confpath,
           '/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/MacOS/Dofus']


def launchDofus():
    """to interrupt : dofus.terminate()"""
    return subprocess.Popen(' '.join(command), shell=True, stderr=subprocess.PIPE)

if __name__ == '__main__':
    dofus = launchDofus()
