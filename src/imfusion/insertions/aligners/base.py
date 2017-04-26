# -*- coding: utf-8 -*-
"""Implements base Aligner classes, used for identifying fusions/insertions."""

# pylint: disable=wildcard-import,redefined-builtin,unused-wildcard-import
from __future__ import absolute_import, division, print_function
from builtins import *
# pylint: enable=wildcard-import,redefined-builtin,unused-wildcard-import

import logging

import pathlib2 as pathlib

from imfusion.external.util import check_dependencies

_aligner_registry = {}


def register_aligner(name, aligner):
    """Registers aligner under given name."""
    _aligner_registry[name] = aligner


def get_aligners():
    """Returns all registered aligners."""
    return dict(_aligner_registry)


class Aligner(object):
    """Base aligner class.

    This base class defines the interface for ``Aligner`` classes. The main
    methods provided by ``Aligners`` are the ``check_dependencies`` and
    ``identify_insertions`` methods. The former is used to check whether
    required external dependencies are present in ``$PATH``, whilst the latter
    should be called with a reference instance and the sequence read files
    to identify insertions. The implementation of the ``identify_insertions``
    method is specific to each aligner and should be overridden in each
    subclass.

    Parameters
    ----------
    reference : Reference
        Reference class describing the reference paths.
    logger : logging.Logger
        Logger to be used for logging messages.

    """

    def __init__(self, reference, logger=None):
        self._reference = reference
        self._logger = logger or logging.getLogger()

    @property
    def dependencies(self):
        """External dependencies required by aligner."""
        return []

    def check_dependencies(self):
        """Checks if all required external dependencies are in ``$PATH``.

        Raises a ValueError if any dependencies are missing.
        """
        check_dependencies(self.dependencies)

    @classmethod
    def configure_args(cls, parser):
        """Configures an argument parser for the Indexer.

        Used by ``imfusion-build`` to configure the sub-command for
        this indexer (if registered as an Indexer using the
        ``register_indexer`` function).

        Parameters
        ----------
        parser : argparse.ArgumentParser
            Argument parser to configure.

        """

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
    def _parse_args(cls, args):
        """Parses arguments from argparse into a dict."""
        return {}

    @classmethod
    def from_args(cls, args):
        """Constructs an Indexer instance from given arguments.

        Instantiates an Indexer instance from the given argparse arguments.
        Uses the ``_parse_args`` method internally, which performs the actual
        argument-to-parameter extraction. As such, the ``_parse_args`` method
        should be overridden in any subclasses with extra parameters.

        Parameters
        ----------
        args : argparse.Namespace
            Arguments to parse.
        """
        return cls(**cls._parse_args(args))

    def identify_insertions(self, fastq_path, output_dir, fastq2_path=None):
        """Identifies insertions from given reads.

        Aligns RNA-seq reads to the reference genome and uses this alignment
        to identify gene-transposon fusions. These gene-transposon fusions
        are summarized to transposon insertions and returned.

        Parameters
        ----------
        fastq_path : Path
            Path to fastq file containing sequence reads. For paired-end data,
            this should refer to the first read of the pair.
        output_dir : Path
            Output directory, to use for output files such as the alignment.
        fastq2_path : Path
            For paired-end sequencing data, path to fastq file containing
            the second read of the pair.

        Yields
        ------
        Insertion
            Yields the identified insertions.
        """

        raise NotImplementedError()
