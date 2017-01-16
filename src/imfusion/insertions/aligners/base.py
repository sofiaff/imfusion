# pylint: disable=W0622,W0614,W0401
from __future__ import absolute_import, division, print_function
from builtins import *
# pylint: enable=W0622,W0614,W0401

import logging

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from imfusion.util import shell

_aligner_registry = {}


def register_aligner(name, aligner):
    """Registers aligner under given name."""
    _aligner_registry[name] = aligner


def get_aligners():
    """Returns all registered aligners."""
    return dict(_aligner_registry)


class Aligner(object):
    """Basic aligner class."""

    def __init__(self, reference, logger=None):
        self._reference = reference
        self._logger = logger or logging.getLogger()

    @property
    def dependencies(self):
        """External dependencies required by aligner."""
        return []

    def check_dependencies(self):
        """Checks if all required external dependencies are available."""
        shell.check_dependencies(self.dependencies)

    @classmethod
    def configure_args(cls, parser):
        """Configures argument parser for aligner."""

        # Required arguments.
        base_group = parser.add_argument_group('Basic arguments')

        base_group.add_argument(
            '--fastq',
            type=pathlib.Path,
            required=True,
            help='Path(s) to the samples fastq files.')

        base_group.add_argument(
            '--fastq2',
            type=pathlib.Path,
            default=None,
            help='Paths to the second pair fastq files (for paired-end '
            'sequencing data). Should be given in the same order as for fastq.')

        base_group.add_argument(
            '--reference',
            type=pathlib.Path,
            required=True,
            help='Path to the index of the augmented reference '
            'generated by im-fusion build.')

        base_group.add_argument(
            '--output_dir',
            required=True,
            type=pathlib.Path,
            help='The samples output directory.')

    @classmethod
    def parse_args(cls, args):
        """Parses arguments from argparse into a dict."""
        raise NotImplementedError()

    @classmethod
    def from_args(cls, args):
        """Constructs aligner instance from argparse arguments."""
        return cls(**cls.parse_args(args))

    def identify_insertions(self, fastq_path, output_dir, fastq2_path=None):
        """Identifies insertions from given reads."""

        raise NotImplementedError()
