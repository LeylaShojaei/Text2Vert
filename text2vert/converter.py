#!/usr/bin/python3

"""
This script converts text files to vertical files, required by NoSketch Engine.
"""

import argparse
import logging
import os
import os.path
import string
import sys

from typing import List


_logger = logging.getLogger(__name__)
_LOGGING_FORMAT = "%(asctime)s - %(module)s [%(levelname)s]: %(message)s"
_LOGGING_LEVEL = logging.INFO
_PUNCTUATION_CHARS = string.punctuation


def _argument_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument("--debug",
                   dest="debug",
                   action="store_true",
                   help="set logging level to debug")
    p.add_argument("raw_text_file_path",
                   type=str,
                   help="Path to the raw text file that contains the corpus")
    p.add_argument("nosketch_directory_path",
                   type=str,
                   help="Path to NoSketch Engine docker directory")
    p.add_argument("corpus_name",
                   type=str,
                   help="Name for the corpus; this is the name that will be"
                        " displayed on the user interface.")
    return p


def _convert_text_to_vert(raw_text: str) -> List[str]:
    words = raw_text.split()
    result = []

    for word in words:
        word_split = _split_word(word)
        result.extend(word_split)

    return result


def _create_corpus_directory(nosketch_docker_path: str, corpus_name: str) -> str:
    if not nosketch_docker_path.endswith("/"):
        nosketch_docker_path += "/"

    if not os.path.exists(nosketch_docker_path):
        _logger.error("The provided path "
                      f"('{nosketch_docker_path}') does not exist.")
        sys.exit(-1)

    corpus_path = nosketch_docker_path + "corpora/" + corpus_name.lower()
    try:
        os.mkdir(corpus_path, mode=0o755)
    except FileExistsError:
        _logger.error("The corpus "
                      f"('{corpus_name}', path={corpus_path}) already exists.")
        sys.exit(-1)

    vertical_path = corpus_path + "/vertical"
    os.mkdir(vertical_path, mode=0o755)

    return vertical_path


def _create_registry_file(nosketch_docker_path: str, corpus_name: str):
    if not nosketch_docker_path.endswith("/"):
        nosketch_docker_path += "/"

    if not os.path.exists(nosketch_docker_path):
        _logger.error("The provided path "
                      f"('{nosketch_docker_path}') does not exist.")
        sys.exit(-1)

    registry_file_path = nosketch_docker_path \
                         + "corpora/registry/" \
                         + corpus_name.lower()

    registry_content = (
        f"NAME \"{corpus_name}\"\n",
        f"PATH {corpus_name.lower()}\n",
        "ENCODING \"UTF-8\"\n",
        "LANGUAGE \"English\"\n",
        "\n",
        f"PATH   '/corpora/{corpus_name.lower()}/indexed/'\n",
        f"VERTICAL  '/corpora/{corpus_name.lower()}/vertical/source'\n",
        "\n",
        "\n",
        "ATTRIBUTE  word\n",
        "\n",
        "STRUCTURE doc {\n",
        # "    ATTRIBUTE title\n",
        "    LABEL \"Corpus Document\"\n",
        "}\n",
    )

    _logger.debug(f"Writing the registry file to:'{registry_file_path}'")
    with open(registry_file_path, "w", encoding="iso_8859_1") as f:
        f.writelines(registry_content)


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

    if "/" in parsed_args.corpus_name:
        _logger.error("The name of the corpus may not contain '/'.")
        sys.exit(-1)

    raw_text = _read_text(parsed_args.raw_text_file_path)

    lines = _convert_text_to_vert(raw_text)

    _logger.debug(f"Lines: {lines[:100]}")

    vertical_path = _create_corpus_directory(parsed_args.nosketch_directory_path,
                                             parsed_args.corpus_name)

    _write_vert(lines, vertical_path)

    _create_registry_file(parsed_args.nosketch_directory_path,
                          parsed_args.corpus_name)


def _read_text(raw_text_path: str) -> str:
    _logger.debug(f"Reading the text file from:'{raw_text_path}'")
    with open(raw_text_path, "r", encoding="iso_8859_1") as f:
        text = f.read()
    return text


def _split_word(word: str) -> List[str]:
    splits = []
    last_cut_i = 0

    for i, character in enumerate(word):
        if character in _PUNCTUATION_CHARS:
            splits.append(word[last_cut_i:i] + "\n")
            splits.append(character + "\n")
            last_cut_i = i + 1

    if last_cut_i < len(word):
        splits.append(word[last_cut_i:] + "\n")

    return splits


def _write_vert(vert_content: List[str], vertical_path: str):
    vertical_path += "/source"

    _logger.debug(f"Writing the vertical file to:'{vertical_path}'")
    with open(vertical_path, "w", encoding="iso_8859_1") as f:
        f.write("<doc>\n")
        f.writelines(vert_content)
        f.write("</doc>\n")


if __name__ == "__main__":
    main()
