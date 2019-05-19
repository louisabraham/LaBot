#!/usr/bin/env python3

from pathlib import Path
import frida

# frida.spawn("/Applications/Dofus.app/Contents/Data/Dofus.app/Contents/MacOS/Dofus")

SCRIPT = (Path(__file__).parent / "script.js").read_text()

session = frida.attach("dofus")

script = session.create_script(SCRIPT)
script.load()
