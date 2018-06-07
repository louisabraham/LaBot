from .binrw import Data, Buffer
from .. import protocol
from ..logs import logger


class Msg:

    def __init__(self, m_id, data, count=None):
        self.id = m_id
        self.data = data
        self.count = count
        logger.debug("Initialized Msg with id {}".format(self.id))

    def __str__(self):
        ans = str.format("{}(id={}, data={}, count={})",
                         self.__class__.__name__,
                         self.id,
                         self.data,
                         self.count)
        return ans
    def __repr__(self):
        ans = str.format("{}(id={}, data={!r}, count={})",
                         self.__class__.__name__,
                         self.id,
                         self.data,
                         self.count)
        return ans

    @staticmethod
    def fromRaw(buf, from_client):
        """Read a message from the buffer and
        empty the beginning of the buffer.
        """
        logger.debug("Trying to parse message from raw buffer...")
        try:
            header = buf.readUnsignedShort()
            if from_client:
                count = buf.readUnsignedInt()
            else:
                count = None
            lenData = int.from_bytes(buf.read(header & 3), 'big')
            id = header >> 2
            logger.debug("Message has id {}".format(id))
            data = Data(buf.read(lenData))
        except IndexError:
            buf.pos = 0
            logger.debug("Could not parse message: Not complete")
            return None
        else:
            if id == 2:
                logger.debug(
                    "Message is NetworkDataContainerMessage! Uncompressing...")
                newbuffer = Buffer(data.readByteArray())
                newbuffer.uncompress()
                msg = Msg.fromRaw(newbuffer, from_client)
                assert msg is not None and not newbuffer.remaining()
                return msg
            logger.debug("Parsed message with ID {}".format(id))
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
        ans += len(self.data).to_bytes(self.lenlenData(), 'big')
        ans += self.data
        return ans.data

    @property
    def msgType(self):
        return protocol.msg_from_id[self.id]

    def json(self):
        logger.debug(
            "Getting json representation of message with id %s", self.id)
        if not hasattr(self, 'parsed'):
            try:
                self.parsed = protocol.read(self.msgType, self.data)
            except IndexError:
                logger.error("Index error for message")
        return self.parsed

    @staticmethod
    def from_json(json, count=None):
        type = json['__type__']
        id = protocol.types[type]['protocolId']
        data = protocol.write(type, json)
        return Msg(id, data, count)

