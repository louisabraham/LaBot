from .network.bridge import Bridge, PrintingBridgeHandler, PrintingMsgBridgeHandler

def main(coJeu, coServ):
    Bridge(coJeu, coServ, PrintingMsgBridgeHandler).run()