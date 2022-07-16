#!/usr/bin/python3

"""
This script converts claws files to vertical files, required by NoSketch Engine.
"""

import argparse
import logging

from typing import List


_logger = logging.getLogger(__name__)
_LOGGING_FORMAT = "%(asctime)s - %(module)s [%(levelname)s]: %(message)s"
_LOGGING_LEVEL = logging.INFO


def _argument_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--debug",
                   dest="debug",
                   action="store_true",
                   help="set logging level to debug")
    p.add_argument("claws_path",
                   type=str,
                   help="Path to the CLAWS file")
    return p


def main():
    parsed_args = _argument_parser().parse_args()

    if parsed_args.debug:
        logging.basicConfig(format=_LOGGING_FORMAT,
                            level=logging.DEBUG)
    else:
        logging.basicConfig(format=_LOGGING_FORMAT,
                            level=_LOGGING_LEVEL)

    _logger.debug("This is a debug message")
    _logger.info("This is an info message")
    claws_rows = _read_claws(parsed_args.claws_path)


def _read_claws(claws_path: str) -> List[str]:
    _logger.debug(f"Reading the CLAWS file from:'{claws_path}'")
    with open(claws_path, "r") as f:
        rows = f.readlines()
    return rows


if __name__ == "__main__":
    main()
