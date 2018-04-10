from os import path
from uuid import uuid4 as uuid
from pprint import pformat

import asyncio
import threading

from wdom.document import get_document, set_app
from wdom.server import start_server, start

from wdom.themes import bootstrap3

from wdom.themes.bootstrap3 import *


class SnifferUI(Div):
    def __init__(self, startfun, *args, **kwargs):
        self.startfun = startfun
        self.stopfun = None
        super().__init__(*args, **kwargs)

        self.append(H1('LaBot sniffer', style='text-align: center;'))

        self.button_wrapper = Div(parent=self)

        startbutton = SuccessButton('start', parent=self.button_wrapper)
        startbutton.addEventListener('click', self.start)

        stopbutton = DangerButton('stop', parent=self.button_wrapper)
        stopbutton.addEventListener('click', self.stop)

        self.info = P('Press start', parent=self.button_wrapper)

        self.msgtable = MsgTable(parent=self)

    def start(self, event):
        # TODO: display message
        if self.stopfun is None:
            self.stopfun = self.startfun(self.msgtable.appendMsg)
            self.info.textContent = 'Sniffer started'
        else:
            self.info.textContent = 'Sniffer already started'

    def stop(self, event):
        if self.stopfun is not None:
            self.stopfun()
            self.stopfun = None
            self.info.textContent = 'Sniffer stopped'
        else:
            self.info.textContent = 'Sniffer already stopped'


class MsgTable(Table):
    def __init__(self, *args, **kwargs):
        super().__init__(class_='table-hover', *args, **kwargs)
        self.thead = Thead(parent=self)
        self.tr1 = Tr(parent=self.thead)
        self.tr1.append(
            Th('Count', class_="col-sm-1"),
            Th('Name', class_="col-sm-3"),
            Th('id', class_="col-sm-1"),
            Th('length', class_="col-sm-1"),
            Th('contents')
        )
        self.tbody = Tbody(parent=self)

    def appendMsg(self, msg):
        Msg(msg, parent=self.tbody)


class Msg(Tr):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        if msg.count is not None:
            super().__init__(class_='success', *args, **kwargs)
        else:
            super().__init__(class_='info', *args, **kwargs)
        self.addEventListener('click', self.switch_view)

        self.contents = Td('', style='white-space: pre;')
        self.append(
            Td(str(msg.count)),
            Td(msg.msgType['name']),
            Td(str(msg.id)),
            Td(str(len(msg.data))),
            self.contents
        )

    def switch_view(self, event):
        if not self.contents.textContent:
            self.contents.textContent = pformat(self.msg.json())
        else:
            self.contents.textContent = ''


document = get_document()
document.register_theme(bootstrap3)
document.add_jsfile('https://unpkg.com/sticky-table-headers')


def init(start):
    global ui
    ui = SnifferUI(start)
    set_app(ui)


def loop_in_thread(loop):
    asyncio.set_event_loop(loop)
    start()


def async_start():
    loop = asyncio.get_event_loop()
    t = threading.Thread(target=loop_in_thread, args=(loop,))
    t.start()


if __name__ == '__main__':
    init(None)
    async_start()
    from collections import namedtuple
    MMsg = namedtuple('Msg', 'id count data')
    ui.msgtable.appendMsg(MMsg('abcd', 'zjenzajn', 'jdnjnejnr'))
