"""Command line interfaces for unblocking Workers"""

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
    '-f', '--file',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to file of WorkerIds to block.")
@click.option(
    '--reason', '-r',
    default="Worker was blocked by mistake.",
    help='Reason for blocking worker(s) (workers do not see).')
@click.option(
    '--live', '-l',
    is_flag=True,
    help='View the status of HITs from the live MTurk site.')
def unblock_workers(file, ids, reason, live):
    """Unblock workers by WorkerId.

    Given a space seperated list of WorkerIds and/or a path to
    a CSV of WorkerIds, remove a block for each worker listed.

    Parameters:
        - ids: Space separated list of WorkerIds to block.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    worker_ids = list(ids)

    # read ids from file (adds to provided ids)
    if file is not None:
       worker_ids += utils.workers.read_workerids_from_file(file) 

    # remove blocks
    for worker_id in worker_ids:
        logger.info(f'Removing block for worker {worker_id}.')
        response = client.delete_worker_block(
            WorkerId=worker_id,
            Reason=reason
        )

    logger.info('Finished removing blocks.')