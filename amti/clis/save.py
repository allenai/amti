"""Command line interfaces for saving HITs"""

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
    help='Save HITs from the live MTurk site.')
def save_batch(batch_dir, live):
    """Save results from the batch of HITs defined in BATCH_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs with
    HITs out in MTurk, all of which have been reviewed and either
    approved or rejected, collect the results and save them into
    BATCH_DIR.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    actions.save.save_batch(
        client=client,
        batch_dir=batch_dir)

    logger.info('Finished saving batch.')
