"""Command line interfaces for blocking Workers"""

import logging

import click
from amti import utils

logger = logging.getLogger(__name__)


@click.command(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
@click.option(
    '--live', '-l',
    is_flag=True,
    help='View the status of HITs from the live MTurk site.')
def list_blocked(live):
    """Block workers by WorkerId.

    Given a space seperated list of WorkerIds (IDS) and/or a path to
    a CSV of WorkerIds, create a block for each worker in the list.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    # listing workers ids
    logger.info(f'Listing the blocked workers (max={max}).')
    response = client.list_worker_blocks(MaxResults=100)
    if response['NumResults'] == 0:
        logger.info("No one is blocked! ")
    else:
        logger.info("List of blocked workers: ")
        for w in response['WorkerBlocks']:
            logger.info(f" -> {w}")
    logger.info('Finished listing the blocked workers.')
