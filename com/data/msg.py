from .binrw import Data, Buffer


class Msg:

    def __init__(self, id=0, data=Data()):
        self.id = id
        self.data = data

    @staticmethod
    def fromRaw(buf):
        '''Forme un message à partir du buffer en position de lecture initiale et vide le début du buffer.'''
        try:
            header = int.from_bytes(buf.read(2), 'big')
            lenData = int.from_bytes(buf.read(header & 3), 'big')
            id = header >> 2
            data = Data(buf.read(lenData))
        except IndexError:
            buf.pos = 0
            return None
        else:
            buf.end()
            return Msg(id, data)

    def lenlenData(self):
        if len(self.data) > 65535:
            return 3
        if len(self.data) > 255:
            return 2
        if lens(self.data) > 0:
            return 1

    def bytes(self):
        header = 4 * self.id + self.lenlenData()
        return header.to_bytes(2, 'big') + len(self.data).to_bytes(self.lenlenData(), 'big') + self.data
