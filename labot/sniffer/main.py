from sniffer.network import launch_in_thread
import sniffer.ui
import argparse


def main(capture_file=None):
    sniffer.ui.init(launch_in_thread, capture_file)
    sniffer.ui.async_start()


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