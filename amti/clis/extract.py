"""Command line interfaces for extracting data from a batch"""

import logging

import click

# import extraction directly to avoid a circular import
from amti.clis import extraction


logger = logging.getLogger(__name__)


@click.group(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
def extract():
    """Extract data from a batch to various formats.

    See the subcommands for extracting batch data into a specific
    format.
    """
    pass


subcommands = [
    # tabular
    extraction.tabular.tabular,
    # xml
    extraction.xml.xml
]

for subcommand in subcommands:
    extract.add_command(subcommand)


if __name__ == '__main__':
    extract()
