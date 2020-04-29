from zlib import decompress
import struct

"""
Replicate com.ankamagames.jerakine.network.CustomDataWrapper
"""


class Data:
    def __init__(self, data=None):
        if data is None:
            data = bytearray()
        self.data = data
        self.pos = 0

    def __len__(self):
        return len(self.data)

    def __add__(self, byte):
        return self.data + byte

    def __radd__(self, byte):
        return byte + self.data

    def __iadd__(self, by):
        self.data += by
        return self

    def __str__(self):
        return str.format(
            "{}(bytearray.fromhex('{}'))", self.__class__.__name__, self.data.hex()
        )

    def __repr__(self):
        return str.format("{}({!r})", self.__class__.__name__, self.data)

    def remaining(self):
        return len(self) - self.pos

    def hex(self):
        return self.data.hex()

    @classmethod
    def fromhex(cls, hex):
        return cls(bytearray.fromhex(hex))

    def verif(self, l):
        if len(self) < self.pos + l:
            raise IndexError(self.pos, l, len(self))

    def reset_pos(self):
        self.pos = 0

    def read(self, l):
        self.verif(l)
        pos = self.pos
        self.pos += l
        return self.data[pos : pos + l]

    def write(self, l):
        self.data += l

    def uncompress(self):
        self.data = bytearray(decompress(self.data))

    def readBoolean(self):
        ans = self.read(1)
        assert ans[0] in [0, 1]
        return bool(ans[0])

    def writeBoolean(self, b):
        if b:
            self.data += b"\x01"
        else:
            self.data += b"\x00"

    def readByte(self):
        return int.from_bytes(self.read(1), "big", signed=True)

    def writeByte(self, b):
        self.data += b.to_bytes(1, "big", signed=True)

    def readByteArray(self):
        lon = self.readVarInt()
        return self.read(lon)

    def writeByteArray(self, ba):
        self.writeVarInt(len(ba))
        self.data += ba

    def readDouble(self):
        return struct.unpack("!d", self.read(8))[0]

    def writeDouble(self, d):
        self.data += struct.pack("!d", d)

    def readFloat(self):
        return struct.unpack("!f", self.read(4))[0]

    def writeFloat(self, f):
        self.data += struct.pack("!f", f)

    def readInt(self):
        return int.from_bytes(self.read(4), "big", signed=True)

    def writeInt(self, i):
        self.data += i.to_bytes(4, "big", signed=True)

    def readShort(self):
        return int.from_bytes(self.read(2), "big", signed=True)

    def writeShort(self, s):
        self.data += s.to_bytes(2, "big", signed=True)

    def readUTF(self):
        lon = self.readUnsignedShort()
        return self.read(lon).decode()

    def writeUTF(self, ch):
        dat = ch.encode()
        self.writeUnsignedShort(len(dat))
        self.data += dat

    def readUnsignedByte(self):
        return int.from_bytes(self.read(1), "big")

    def writeUnsignedByte(self, b):
        self.data += b.to_bytes(1, "big")

    def readUnsignedInt(self):
        return int.from_bytes(self.read(4), "big")

    def writeUnsignedInt(self, ui):
        self.data += ui.to_bytes(4, "big")

    def readUnsignedShort(self):
        return int.from_bytes(self.read(2), "big")

    def writeUnsignedShort(self, us):
        self.data += us.to_bytes(2, "big")

    def _writeVar(self, i):
        if not i:
            self.writeUnsignedByte(0)
        while i:
            b = i & 0b01111111
            i >>= 7
            if i:
                b |= 0b10000000
            self.writeUnsignedByte(b)

    def readVarInt(self):
        ans = 0
        for i in range(0, 32, 7):
            b = self.readUnsignedByte()
            ans += (b & 0b01111111) << i
            if not b & 0b10000000:
                return ans
        raise Exception("Too much data")

    def writeVarInt(self, i):
        assert i.bit_length() <= 32
        self._writeVar(i)

    def readVarUhInt(self):
        return self.readVarInt()

    def writeVarUhInt(self, i):
        self.writeVarInt(i)

    def readVarLong(self):
        ans = 0
        for i in range(0, 64, 7):
            b = self.readUnsignedByte()
            ans += (b & 0b01111111) << i
            if not b & 0b10000000:
                return ans
        raise Exception("Too much data")

    def writeVarLong(self, i):
        assert i.bit_length() <= 64
        self._writeVar(i)

    def readVarUhLong(self):
        return self.readVarLong()

    def writeVarUhLong(self, i):
        self.writeVarLong(i)

    def readVarShort(self):
        ans = 0
        for i in range(0, 16, 7):
            b = self.readByte()
            ans += (b & 0b01111111) << i
            if not b & 0b10000000:
                return ans
        raise Exception("Too much data")

    def writeVarShort(self, i):
        assert i.bit_length() <= 16
        self._writeVar(i)

    def readVarUhShort(self):
        return self.readVarShort()

    def writeVarUhShort(self, i):
        self.writeVarShort(i)


class Buffer(Data):
    def end(self):
        """Very efficient
        """
        del self.data[: self.pos]
        self.pos = 0

    def reset(self):
        self.__init__()
import logging



logger = logging.getLogger("labot")


class Msg:
    def __init__(self, m_id, data, count=None):
        self.id = m_id
        if isinstance(data, bytearray):
            data = Data(data)
        self.data = data
        self.count = count
        # logger.debug("Initialized Msg with id {}".format(self.id))

    def __str__(self):
        ans = str.format(
            "{}(m_id={}, data={}, count={})",
            self.__class__.__name__,
            self.id,
            self.data.data,
            self.count,
        )
        return ans

    def __repr__(self):
        ans = str.format(
            "{}(m_id={}, data={!r}, count={})",
            self.__class__.__name__,
            self.id,
            self.data.data,
            self.count,
        )
        return ans

    @staticmethod
    def fromRaw(buf: Buffer, from_client):
        """Read a message from the buffer and
        empty the beginning of the buffer.
        """
        if not buf:
            return
        try:
            header = buf.readUnsignedShort()
            if from_client:
                count = buf.readUnsignedInt()
            else:
                count = None
            lenData = int.from_bytes(buf.read(header & 3), "big")
            id = header >> 2
            data = Data(buf.read(lenData))
        except IndexError:
            buf.pos = 0
            logger.debug("Could not parse message: Not complete")
            return None
        else:
            if id == 2:
                logger.debug("Message is NetworkDataContainerMessage! Uncompressing...")
                newbuffer = Buffer(data.readByteArray())
                newbuffer.uncompress()
                msg = Msg.fromRaw(newbuffer, from_client)
                assert msg is not None and not newbuffer.remaining()
                return msg
#            logger.debug("Parsed %s", msg_from_id[id]["name"])
            buf.end()

            return Msg(id, data, count)

    def lenlenData(self):
        if len(self.data) > 65535:
            return 3
        if len(self.data) > 255:
            return 2
        if len(self.data) > 0:
            return 1
        return 0

    def bytes(self):
        header = 4 * self.id + self.lenlenData()
        ans = Data()
        ans.writeShort(header)
        if self.count is not None:
            ans.writeUnsignedInt(self.count)
        ans += len(self.data).to_bytes(self.lenlenData(), "big")
        ans += self.data
        return ans.data

    @property
    def msgType(self):
        return msg_from_id[self.id]

    def json(self):
        logger.debug("Getting json representation of message %s", self)
        if not hasattr(self, "parsed"):
            self.parsed = read(self.msgType, self.data)
        return self.parsed

    @staticmethod
    def from_json(json, count=None, random_hash=True):
        type_name: str = json["__type__"]
        type_id: int = types[type_name]["protocolId"]
        data = write(type_name, json, random_hash=random_hash)
        return Msg(type_id, data, count)

from js import types, msg_from_id, types_from_id, primitives
from functools import reduce
import logging
import random
from zlib import decompress



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

