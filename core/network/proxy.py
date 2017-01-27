from socketserver import ThreadingMixIn
from http.server import HTTPServer, BaseHTTPRequestHandler
import socket
from threading import Thread

from .bridge import Bridge, PrintingBridgeHandler
from .. import main

connection_servers = ['213.248.126.39', '213.248.126.40']


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    debug = False


class ProxyRequestHandler(BaseHTTPRequestHandler):

    def do_CONNECT(self):
        address = self.path.split(':', 1)
        address[1] = int(address[1]) or 443
        try:
            s = socket.create_connection(address, timeout=self.timeout)
        except Exception as e:
            self.send_error(502)
            return
        self.send_response(200, 'Connection Established')
        self.end_headers()

        # Here the main function is launched
        main(self.connection, s)
        # It MUST run in sync mode (not threaded)
        # The bot will run in sync mode and will have a Bridge in async
        # You can use the condition
        # if address[0] not in connection_servers
        # to start your bot only after the connexion

        # VERY IMPORTANT
        self.close_connection = True

    def log_message(self, format, *args):
        """To avoid silly debug messages"""
        if self.server.debug:
            super().log_message(format, *args)


def startProxyServer(port=8000):
    httpd = ThreadingHTTPServer(('localhost', port), ProxyRequestHandler)
    Thread(None, httpd.serve_forever).start()
    return httpd
