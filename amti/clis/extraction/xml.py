"""Command line interface for extracting XML from a batch"""

import logging

import click

from amti import actions


logger = logging.getLogger(__name__)


@click.command(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
@click.argument(
    'batch_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument(
    'output_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
def xml(batch_dir, output_dir):
    """Extract XML data from assignments in BATCH_DIR to OUTPUT_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs that
    have been reviewed and saved, extract the XML data from the
    assignments to OUTPUT_DIR.
    """
    actions.extraction.xml.xml(
        batch_dir=batch_dir,
        output_dir=output_dir)
