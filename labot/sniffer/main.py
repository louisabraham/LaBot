from .network import launch_in_thread
from . import ui
import argparse

from ..logs import logger


def main(capture_file=None):
    ui.init(launch_in_thread, capture_file)
    ui.async_start()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Start the sniffer either from a file or from live capture.')
    parser.add_argument('--capture', '-c', metavar='PATH', type=str,
                        help='Path to capture file')
    parser.add_argument('--debug', '-d', action='store_true',
                        help='show logger debug messages')

    args = parser.parse_args()    

    if(args.debug):
        logger.setLevel("DEBUG")
    else:
        logger.setLevel("INFO")

    if args.capture:
        logger.debug("Starting sniffer with capture file")
        main(args.capture)
    else:
        logger.debug("Starting sniffer on live interface")
        main()
