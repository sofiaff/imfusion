# -*- coding: utf-8 -*-
"""Implements indexer for building Tophat references."""

# pylint: disable=wildcard-import,redefined-builtin,unused-wildcard-import
from __future__ import absolute_import, division, print_function
from builtins import *
# pylint: enable=wildcard-import,redefined-builtin,unused-wildcard-import

import tempfile
import shutil

try:
    import pathlib
except ImportError:
    import pathlib2 as pathlib

from imfusion.util import shell

from .base import Indexer, register_indexer, Reference


class TophatIndexer(Indexer):
    """Indexer that builds references for the Tophat-Fusion aligner.

    Performs the same steps as the base ``Indexer`` class, but additionally
    generates an index for alignment with Tophat-Fusion using Bowtie and
    Tophat2.
    """

    def __init__(self, logger=None):
        super().__init__(logger=logger)

    @property
    def _reference_class(self):
        """Reference class to use for this indexer."""
        return TophatReference

    @property
    def dependencies(self):
        """External dependencies required by this indexer."""
        return ['bowtie-build', 'tophat2']

    def _build_indices(self, reference):
        # type: (TophatReference) -> None

        # Build bowtie index.
        self._logger.info('Building bowtie index')

        bowtie_idx_path = reference.index_path
        bowtie_log_path = reference.base_path / 'bowtie.log'
        self._build_bowtie_index(
            reference.fasta_path, bowtie_idx_path, log_path=bowtie_log_path)

        # Build transcriptome index.
        self._logger.info('Building transcriptome index')
        transcriptome_path = reference.transcriptome_path
        transcriptome_log_path = reference.base_path / 'transcriptome.log'
        self._build_transcriptome_index(bowtie_idx_path, reference.gtf_path,
                                        transcriptome_path,
                                        transcriptome_log_path)

    @staticmethod
    def _build_bowtie_index(
            reference_path,  # type: pathlib.Path
            output_base_path,  # type: pathlib.Path
            log_path=None  # type: pathlib.Path
    ):
        """
        Builds a bowtie index for a reference genome.

        Parameters
        ----------
        reference_path : pathlib.Path
            Path to the reference genome.
        out_base_path : pathlib.Path
            Base output path for the built index.
        log_path : pathlib.Path
            Where to write the log output.

        """

        cmdline_args = [
            'bowtie-build', str(reference_path), str(output_base_path)
        ]

        if log_path is not None:
            with log_path.open('w') as log_file:
                shell.run_command(args=cmdline_args, stdout=log_file)
        else:
            shell.run_command(args=cmdline_args)

    @staticmethod
    def _build_transcriptome_index(
            index_path,  # type: pathlib.Path
            gtf_path,  # type: pathlib.Path
            output_base_path,  # type: pathlib.Path
            log_path=None  # type: pathlib.Path
    ):  # type:  (...) -> None
        """
        Builds a transcriptome index for a reference genome.

        Parameters
        ----------
        reference_path : pathlib.Path
            Path to the reference genome.
        gtf_path : pathlib.Path
            Path to the reference gtf file.
        out_base_path pathlib.Path:
            Base output path for the built index.
        log_path : pathlib.Path
            Where to write the log output.


        """

        tmp_dir = tempfile.mkdtemp()

        try:
            cmdline_args = [
                'tophat2', '--GTF', str(gtf_path),
                '--transcriptome-index={}'.format(output_base_path),
                '--bowtie1', '--output-dir', str(tmp_dir), str(index_path)
            ]

            if log_path is not None:
                with log_path.open('w') as log_file:
                    shell.run_command(args=cmdline_args, stdout=log_file)
            else:
                shell.run_command(args=cmdline_args)
        finally:
            shutil.rmtree(tmp_dir)


register_indexer('tophat', TophatIndexer)


class TophatReference(Reference):
    """Tophat Reference class.

    Defines paths to files within the Tophat-Fusion reference. Compared to the
    base reference, this class adds an additional path to the transcriptome
    index that is used by Tophat during alignment.
    """

    @property
    def transcriptome_path(self):
        # type: (...) -> pathlib.Path
        """Path to transcriptome index."""
        return self._reference / 'transcriptome'

    @property
    def index_path(self):
        # type: (...) -> pathlib.Path
        """Path to index."""
        return self._reference / 'reference'