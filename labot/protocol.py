from .protocolBuilder import types, msg_from_id, types_from_id, primitives
from .data import Data

primitives = {
    name: (
        getattr(Data, 'read' + name),
        getattr(Data, 'write' + name)
    )
    for name in primitives
}


def readBooleans(type, data):
    ans = dict(__type__=type['name'])
    boolVars = type['boolVars']
    bvars = iter(boolVars)
    for _ in range(0, len(boolVars), 8):
        bits = format(data.readByte(), '08b')[::-1]
        for var, val in zip(bvars, bits):
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
    ans.update(readBooleans(type, data))
    for var in type['vars']:
        if var['length'] is not None:
            ans[var['name']] = readVec(var, data)
        else:
            ans[var['name']] = read(var['type'], data)
    return ans
