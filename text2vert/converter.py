#!/usr/bin/python3

"""
This script converts text files to vertical files, required by NoSketch Engine.
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
    p.add_argument("raw_text_file_path",
                   type=str,
                   help="Path to the raw text file that contains the corpus")
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
    raw_text = _read_text(parsed_args.raw_text_file_path)


def _read_text(raw_text_path: str) -> str:
    _logger.debug(f"Reading the text file from:'{raw_text_path}'")
    with open(raw_text_path, "r", encoding="iso_8859_1") as f:
        text = f.read()
    return text


if __name__ == "__main__":
    main()
