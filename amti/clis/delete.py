"""Command line interfaces for deleting HITs"""

import logging

import click

from amti import actions
from amti import settings
from amti import utils


logger = logging.getLogger(__name__)


@click.command(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
@click.argument(
    'batch_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--live', '-l',
    is_flag=True,
    help='Delete HITs from the live MTurk site.')
def delete_batch(batch_dir, live):
    """Delete the batch of HITs defined in BATCH_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs with
    HITs, delete all the HITs from MTurk.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    actions.delete.delete_batch(client=client, batch_dir=batch_dir)

    logger.info('Finished deleting batch.')
