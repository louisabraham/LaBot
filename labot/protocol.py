from functools import reduce
import logging
import random
from zlib import decompress

from .protocol_load import types, msg_from_id, types_from_id, primitives
from .data import Data, Buffer


logger = logging.getLogger("labot")

primitives = {
    name: (getattr(Data, "read" + name), getattr(Data, "write" + name))
    for name in primitives
}


def readBooleans(boolVars, data):
    ans = {}
    bvars = iter(boolVars)
    for _ in range(0, len(boolVars), 8):
        bits = format(data.readByte(), "08b")[::-1]
        for val, var in zip(bits, bvars):
            # be careful, you have to
            # put bits first in zip
            ans[var["name"]] = val == "1"
    return ans


def readVec(var, data):
    assert var["length"] is not None
    if isinstance(var["length"], int):
        n = var["length"]
    else:
        n = read(var["length"], data)
    ans = []
    for _ in range(n):
        ans.append(read(var["type"], data))
    return ans


def read(type, data: Data):
    if type is False:
        type = types_from_id[data.readUnsignedShort()]
    elif isinstance(type, str):
        if type in primitives:
            return primitives[type][0](data)
        type = types[type]
    logger.debug("reading data %s", data)
    logger.debug("with type %s", type)

    if type["parent"] is not None:
        logger.debug("calling parent %s", type["parent"])
        ans = read(type["parent"], data)
        ans["__type__"] = type["name"]
    else:
        ans = dict(__type__=type["name"])

    logger.debug("reading boolean variables")
    ans.update(readBooleans(type["boolVars"], data))
    logger.debug("remaining data: %s", data.data[data.pos :])

    for var in type["vars"]:
        logger.debug("reading %s", var)
        if var["optional"]:
            if not data.readByte():
                continue
        if var["length"] is not None:
            ans[var["name"]] = readVec(var, data)
        else:
            ans[var["name"]] = read(var["type"], data)
        logger.debug("remaining data: %s", data.data[data.pos :])
    if type["hash_function"] and data.remaining() == 48:
        ans["hash_function"] = data.read(48)
    return ans


def writeBooleans(boolVars, el, data):
    bits = []
    for var in boolVars:
        bits.append(el[var["name"]])
        if len(bits) == 8:
            data.writeByte(reduce(lambda a, b: 2 * a + b, bits[::-1]))
            bits = []
    if bits:
        data.writeByte(reduce(lambda a, b: 2 * a + b, bits[::-1]))


def writeVec(var, el, data):
    assert var["length"] is not None
    n = len(el)
    if isinstance(var["length"], int):
        assert n == var["length"]
    else:
        write(var["length"], n, data)
    for it in el:
        write(var["type"], it, data)


def write(type, json, data=None, random_hash=True) -> Data:
    if data is None:
        data = Data()
    if type is False:
        type = types[json["__type__"]]
        data.writeUnsignedShort(type["protocolId"])
    elif isinstance(type, str):
        if type in primitives:
            primitives[type][1](data, json)
            return data
        type = types[type]
    parent = type["parent"]
    if parent is not None:
        write(parent, json, data)
    writeBooleans(type["boolVars"], json, data)
    for var in type["vars"]:
        if var["optional"]:
            if var["name"] in json:
                data.writeByte(1)
            else:
                data.writeByte(0)
                continue
        if var["length"] is not None:
            writeVec(var, json[var["name"]], data)
        else:
            write(var["type"], json[var["name"]], data)
    if "hash_function" in json:
        data.write(json["hash_function"])
    elif type["hash_function"] and random_hash:
        hash = bytes(random.getrandbits(8) for _ in range(48))
        data.write(hash)
    return data
