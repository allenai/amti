"""Command line interfaces for blocking Workers"""

import logging

import click
import csv

from amti import actions
from amti import settings
from amti import utils


logger = logging.getLogger(__name__)


@click.command(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
@click.argument(
    'ids',
    type=str,
    nargs=-1)
@click.option(
    '--file', '-f',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to file of WorkerIds to block.")
@click.option(
    '--reason', '-r',
    default="Worker has produced low quality work, or is suspected of producing spam.",
    help='Reason for blocking worker(s) (workers do not see).')
@click.option(
    '--live', '-l',
    is_flag=True,
    help='View the status of HITs from the live MTurk site.')
def block_workers(file, ids, reason, live):
    """Block workers by WorkerId.

    Given a space seperated list of WorkerIds (IDS) and/or a path to
    a CSV of WorkerIds, create a block for each worker in the list.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    worker_ids = list(ids)

    # read ids from file (adds to provided ids)
    if file is not None:
       worker_ids += utils.workers.read_workerids_from_file(file) 

    # create blocks
    for worker_id in worker_ids:
        logger.info(f'Creating block for worker {worker_id}.')
        response = client.create_worker_block(
            WorkerId=worker_id,
            Reason=reason
        )

    logger.info('Finished creating blocks.')