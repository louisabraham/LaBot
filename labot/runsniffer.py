import sniffer.main
import argparse

parser = argparse.ArgumentParser(
    description='Start the sniffer either from a file or from live capture.')
parser.add_argument('--capture', '-c', metavar='PATH', type=str,
                    help='Path to capture file')
args = parser.parse_args()
if args.capture:
    sniffer.main.main(args.capture)
else:
    sniffer.main.main()
