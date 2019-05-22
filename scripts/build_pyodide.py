#!/usr/bin/env python3


from pathlib import Path
import pickle
import json


root_path = Path(__file__).absolute().parents[1]
labot_path = root_path / "labot"
docs_path = root_path / "docs"
out_path = docs_path / "main.py"

with (labot_path / "protocol.pk").open("rb") as f:
    types = pickle.load(f)
    msg_from_id = pickle.load(f)
    types_from_id = pickle.load(f)
    primitives = sorted(pickle.load(f))


exports = ["types", "msg_from_id", "types_from_id", "primitives"]
with (docs_path / "protocol.js").open("w") as f:
    for name in exports:
        f.write(f"{name} = ")
        json.dump(eval(name), f)
        f.write("\n")


def apply_transforms(path, out, transforms):
    with open(labot_path / path) as f:
        for l in f:
            for t in transforms:
                l = t(l)
            if l:
                out.write(l)


def eliminate_relative_imports(l):
    return l if not l.startswith("from .") else ""


PROTOCOL_IMPORTS = """from js import types, msg_from_id, types_from_id, primitives
"""
SOURCE = """
import traceback
import json


from js import datatype, content, from_client, out


def main():
    try:
        data = Buffer(bytearray.fromhex(content.value))
        if datatype.value:
            ans = read(datatype.value, data)
        else:
            ans = Msg.fromRaw(data, from_client()).json()
        out.value = json.dumps(ans, indent=4, sort_keys=True)
    except Exception as e:
        out.value = traceback.format_exc()

"""


with open(out_path, "w") as out:
    apply_transforms("data/binrw.py", out, [eliminate_relative_imports])
    apply_transforms(
        "data/msg.py",
        out,
        [eliminate_relative_imports, lambda l: l.replace("protocol.", "")],
    )
    out.write(PROTOCOL_IMPORTS)
    apply_transforms("protocol.py", out, [eliminate_relative_imports])
    out.write(SOURCE)
