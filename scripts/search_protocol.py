#!/usr/bin/env python3

import argparse
import sys
from pathlib import Path
from pprint import pprint

# include path to labot
sys.path.append(Path(__file__).absolute().parents[1].as_posix())

from labot import protocol


def search(types, s):
    def aux(obj):
        if isinstance(obj, str):
            return s in obj.casefold()
        elif isinstance(obj, dict):
            return any(aux(k) or aux(v) for k, v in obj.items())
        elif isinstance(obj, list):
            return any(aux(k) for k in obj)
        else:
            return False

    return [(k, v) for k, v in types.items() if aux(k) or aux(v)]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Search protocol for a string")
    parser.add_argument("search_string")
    args = parser.parse_args()
    pprint(search(protocol.types, args.search_string.casefold()))
