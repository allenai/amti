"""Command line interface for disassociating quals with Workers"""

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
    help="Path to file of WorkerIds.")
@click.option(
    '--qual', '-q', 
    help='QualificationId (or name, if --name flag passed).')
@click.option(
    '--name', '-n',
    is_flag=True,
    help='Search for qual by name instead of id.')
@click.option(
    '--reason', '-r',
    help='Reason for disassociation (worker sees this).')
@click.option(
    '--live', '-l',
    is_flag=True,
    help='View the status of HITs from the live MTurk site.')
def disassociate_qual(file, ids, qual, name, reason, live):
    """Disassociate workers with a qualification.

    Given a space seperated list of WorkerIds (IDS) and/or a path to
    a CSV of WorkerIds, disassociate each worker with a qualification
    (QUAL).

    NOTE: Only works with quals that both exist and are owned by the user.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    worker_ids = list(ids)

    # read ids from file (adds to provided ids)
    if file is not None:
       worker_ids += utils.workers.read_workerids_from_file(file) 

    # set qual_id
    qual_id = qual
    if name:
        qual_id = utils.mturk.get_qual_by_name(client, qual)
        if qual_id is None:
            raise ValueError(f"No qual with name {qual} found.")

    args = {"QualificationTypeId": qual_id}
    if reason is not None:
        args['Reason'] = reason

    # associate qual with workers
    for worker_id in worker_ids:
        logger.info(f'Disassociating qualification {qual_id} from worker {worker_id}.')
        response = client.disassociate_qualification_from_worker(
            WorkerId=worker_id,
            **args
        )

    logger.info('Finished disassociating quals.')