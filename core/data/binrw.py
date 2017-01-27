from zlib import decompress


class Data:

    def __init__(self, data=bytes()):
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
    
    def hex(self):
        return self.data.hex()

    def verif(self, l):
        if len(self) < self.pos + l:
            raise IndexError(self.pos, l, len(self))

    def read(self, l):
        self.verif(l)
        pos = self.pos
        self.pos += l
        return self.data[pos:pos + l]

    def uncompress(self):
        self.data = decompress(self.data)

    def readBoolean(self):
        return bool(self.read(1))

    def readByte(self):
        return int.from_bytes(self.read(1), 'big', signed=True)

    def readUnsignedByte(self):
        return int.from_bytes(self.read(1), 'big')

    def readShort(self):
        return int.from_bytes(self.read(2), 'big', signed=True)

    def readUnsignedShort(self):
        return int.from_bytes(self.read(2), 'big')

    def readInt(self):
        return int.from_bytes(self.read(4), 'big', signed=True)

    def readUnsignedInt(self):
        return int.from_bytes(self.read(4), 'big')

    def readUTF(self):
        lon = self.readUnsignedShort()
        self.pos += lon
        pos = self.pos
        return self.data[pos - lon:pos].decode()

    def readBytes(self, len):
        return self.read(len)

    def writeBoolean(self, b):
        if b:
            self.data += b'\x01'
        else:
            self.data += b'\x00'

    def writeByte(self, b):
        self.data += b.to_bytes(1, 'big', signed=True)

    def writeUnsignedByte(self, b):
        self.data += b.to_bytes(1, 'big')

    def writeShort(self, s):
        self.data += s.to_bytes(2, 'big', signed=True)

    def writeUnsignedShort(self, us):
        self.data += us.to_bytes(2, 'big')

    def writeUnsignedInt(self, ui):
        self.data += ui.to_bytes(4, 'big')

    def writeUTF(self, ch):
        dat = ch.encode()
        self.writeUnsignedShort(len(dat))
        self.data += dat


class Buffer(Data):

    def end(self):
        self.data = self.data[self.pos:]
        self.pos = 0

# class BooleanByteWrapper():
# 	def getFlag(a,pos):
# 		return bool(a&(2**pos))
# 	def getAllFlags(a,nb_pos):
# 		return tuple(BooleanByteWrapper.getFlag(a,pos) for pos in range(nb_pos))
# 	def setFlag(a, pos, b):
# 		if b:
# 			return a|2**pos
# 		else:
# 			return a&~2**pos
# 	def setAllFlags(a,l):
# 		for pos in range(nb_pos):
# 			a=BooleanByteWrapper.setFlag(a, pos, l[pos])
# 		return a
