from data.binrw import Data
import protocol


class Msg:

    def __init__(self, m_id, data, count=None):
        self.id = m_id
        self.data = data
        self.count = count

    def __str__(self):
        return 'Msg(id=%s, data=%s, count=%s)' % (self.id, self.data, self.count)

    @staticmethod
    def fromRaw(buf, from_client):
        """Read a message from the buffer and
        empty the beginning of the buffer.
        """
        try:
            header = buf.readUnsignedShort()
            if from_client:
                count = buf.readUnsignedInt()
            else:
                count = None
            lenData = int.from_bytes(buf.read(header & 3), 'big')
            id = header >> 2
            data = Data(buf.read(lenData))
        except IndexError:
            buf.pos = 0
            return None
        else:
            try:
                buf.end()
                # This wil fail if the buffer comes from 
                # a decompressed NetworkDataContainerMessage
            except TypeError:
                pass
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
        ans += len(self.data).to_bytes(self.lenlenData(), 'big')
        ans += self.data
        return ans.data

    @property
    def msgType(self):
        return protocol.msg_from_id[self.id]

    def json(self):
        if not hasattr(self, 'parsed'):
            self.parsed = protocol.read(self.msgType, self.data)
        return self.parsed

    @staticmethod
    def from_json(json, count=None):
        type = json['__type__']
        id = protocol.types[type]['protocolId']
        data = protocol.write(type, json)
        return Msg(id, data, count)
