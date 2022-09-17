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
    p.add_argument("source_path",
                   type=str,
                   help="Path to the corpus source text. The path can be to the"
                        " raw text file that contains the corpus OR to a"
                        " directory that contains multiple text files that form"
                        " the corpus.")
    p.add_argument("nosketch_directory_path",
                   type=str,
                   help="Path to NoSketch Engine docker directory")
    p.add_argument("corpus_name",
                   type=str,
                   help="Name for the corpus; this is the name that will be"
                        " displayed on the user interface.")
    return p


def _convert_text_to_vert(raw_texts: List[str]) -> List[List[str]]:
    all_docs = []
    for raw_text in raw_texts:
        one_doc = []
        words = raw_text.split()

        for word in words:
            word_split = _split_word(word)
            one_doc.extend(word_split)
        all_docs.append(one_doc)
    return all_docs


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


def _fetch_file_paths(source_path: str):
    """
    TODO: Documentation.
    """
    if os.path.isfile(source_path):
        return [source_path]
    elif os.path.isdir(source_path):
        filenames = os.listdir(source_path)
        all_file_paths = []
        for filename in filenames:
            # Recursion to search all subdirectories.
            full_path = source_path + "/" + filename
            all_file_paths.extend(_fetch_file_paths(full_path))
        return all_file_paths
    else:
        # Should not be reached: Provided source not a file or directory.
        return []


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

    raw_texts = _read_texts(parsed_args.source_path)

    docs = _convert_text_to_vert(raw_texts)

    _logger.debug(f"{len(docs)} documents. First one: {docs[0]}")

    vertical_path = _create_corpus_directory(parsed_args.nosketch_directory_path,
                                             parsed_args.corpus_name)

    _write_vert(docs, vertical_path)

    _create_registry_file(parsed_args.nosketch_directory_path,
                          parsed_args.corpus_name)


def _read_texts(raw_text_path: str) -> List[str]:
    """
    Reads the raw text from the source file(s). The parameter raw_text_path can
    point to either a source text file or a source text file directory. For a
    file, the contents are read and returned as a list of a singular string. For
    a directory, the files within will be read and returned as a list of strings.
    """
    _logger.debug(f"Reading the text file from:'{raw_text_path}'")

    file_paths = _fetch_file_paths(raw_text_path)

    texts = []
    for file_path in file_paths:
        with open(file_path, "r", encoding="iso_8859_1") as f:
            texts.append(f.read())
    return texts


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


def _write_vert(documents: List[List[str]], vertical_path: str):
    vertical_path += "/source"

    _logger.debug(f"Writing the vertical file to:'{vertical_path}'")
    with open(vertical_path, "w", encoding="iso_8859_1") as f:
        for i, doc in enumerate(documents):
            f.write(f"<doc n=\"{i + 1}\">\n")
            f.writelines(doc)
            f.write("</doc>\n")


if __name__ == "__main__":
    main()
