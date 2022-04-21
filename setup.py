#!/usr/bin/env python
import codecs
import os.path
import re

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), "r") as f:
        content = f.read()
    return content


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r'^__version__ = [\'"]([^\'"]*)[\'"]', version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


setup(
    name="typeddict-validator",
    version=find_version("typeddict_validator", "__init__.py"),
    description="Validates Python's TypedDict",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="Sogo Kato",
    url="https://github.com/SogoKato/typeddict-validator",
    packages=find_packages("typeddict_validator"),
    python_requires=">=3.10",
    install_requires=[],
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
)
