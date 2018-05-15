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
    args = parser.parse_args()
    if args.capture:
        main(args.capture)
    else:
        main()