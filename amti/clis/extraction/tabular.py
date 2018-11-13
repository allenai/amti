"""Command line interface for extracting tabular data from a batch"""

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
    'output_path',
    type=click.Path(exists=False, file_okay=True, dir_okay=False))
@click.option(
    '--format', '-f', 'file_format',
    type=click.Choice(
        actions.extraction.tabular.TABULAR_SUPPORTED_FILE_FORMATS),
    default='jsonl',
    help='The desired output file format.')
def tabular(batch_dir, output_path, file_format):
    """Extract data from BATCH_DIR to OUTPUT_PATH in a tabular format.

    Given a directory (BATCH_DIR) that represents a batch of HITs that
    have been reviewed and saved, extract the data to OUTPUT_PATH in a
    tabular format. Every row of the table is an assignment, where each
    form field has a column and also there are additional columns for
    assignment metadata. By default, the table will be saved as JSON
    Lines, but other formats may be specified with the --format option.
    """
    actions.extraction.tabular.tabular(
        batch_dir=batch_dir,
        output_path=output_path,
        file_format=file_format)
