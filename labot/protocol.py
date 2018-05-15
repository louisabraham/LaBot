from functools import reduce

from .protocolBuilder import types, msg_from_id, types_from_id, primitives
from .data import Data, Buffer
from zlib import decompress

primitives = {
    name: (
        getattr(Data, 'read' + name),
        getattr(Data, 'write' + name)
    )
    for name in primitives
}


def readBooleans(boolVars, data):
    ans = {}
    bvars = iter(boolVars)
    for _ in range(0, len(boolVars), 8):
        bits = format(data.readByte(), '08b')[::-1]
        for val, var in zip(bits, bvars):
            # be careful, you have to
            # put bits first in zip
            ans[var['name']] = val == '1'
    return ans


def readVec(var, data):
    assert var['length'] is not None
    if isinstance(var['length'], int):
        n = var['length']
    else:
        n = read(var['length'], data)
    ans = []
    for _ in range(n):
        ans.append(read(var['type'], data))
    return ans


def read(type, data):
    if type is False:
        type = types_from_id[data.readUnsignedShort()]
    elif isinstance(type, str):
        if type in primitives:
            return primitives[type][0](data)
        type = types[type]
    ans = dict(__type__=type['name'])
    parent = type['parent']
    if parent is not None:
        ans.update(read(parent, data))
        ans['__type__'] = type['name']
    ans.update(readBooleans(type['boolVars'], data))
    for var in type['vars']:
        if var['length'] is not None:
            ans[var['name']] = readVec(var, data)
        else:
            ans[var['name']] = read(var['type'], data)
    if type['name'] == "NetworkDataContainerMessage":
        from data import Msg  # Ugly but otherwise we get a circular import
        innerdata = Buffer(ans['content'])
        innerdata.uncompress()
        innerMsg = Msg.fromRaw(innerdata, False)
        ans['innerpacket'] = read(innerMsg.msgType, innerMsg.data)
        print("hello")
    return ans


def writeBooleans(boolVars, el, data):
    bits = []
    for var in boolVars:
        bits.append(el[var['name']])
        if len(bits) == 8:
            data.writeByte(reduce(lambda a, b: 2 * a + b, bits[::-1]))
            bits = []
    if bits:
        data.writeByte(reduce(lambda a, b: 2 * a + b, bits[::-1]))


def writeVec(var, el, data):
    assert var['length'] is not None
    n = len(el)
    if isinstance(var['length'], int):
        assert n == var['length']
    else:
        write(var['length'], n, data)
    for it in el:
        write(var['type'], it, data)


def write(type, json, data=None):
    if data is None:
        data = Data()
    if type is False:
        type = types[json['__type__']]
        data.writeUnsignedShort(type['protocolId'])
    elif isinstance(type, str):
        if type in primitives:
            primitives[type][1](data, json)
            return data
        type = types[type]
    parent = type['parent']
    if parent is not None:
        write(parent, json, data)
    writeBooleans(type['boolVars'], json, data)
    for var in type['vars']:
        if var['length'] is not None:
            writeVec(var, json[var['name']], data)
        else:
            write(var['type'], json[var['name']], data)
    return data
