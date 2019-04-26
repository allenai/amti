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
    '--subject', '-s',
    help='Subject line for message.')
@click.option(
    '--message', '-m',
    help='Text content of message.')
@click.option(
    '--message_file',
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    help="Path to file of WorkerIds to block.")
@click.option(
    '--live', '-l',
    is_flag=True,
    help='View the status of HITs from the live MTurk site.')
def notify_workers(file, ids, subject, message, message_file, live):
    """Send notification message to workers.

    Given a space seperated list of WorkerIds (IDS), or a path to
    a CSV of WorkerIds, send a notification to each worker. 
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    worker_ids = list(ids)

    # read ids from file (adds to provided ids)
    if file is not None:
        worker_ids += utils.workers.read_workerids_from_file(file)

    # create message (file values overrides Subject, Message args)
    message = {'Subject': subject, 'MessageText': message}
    if message_file is not None:
        with open(args.message, 'r') as f:
            message = json.loads(f.read())

    if any(val is None for val in message.values()):
        raise ValueError('Missing Message or Subject value.')

    # break ids into chunks of 100, notify workers in each chunk
    for chunk_ids in utils.workers.chunk_list(worker_ids):

        logger.info(f"Sending notification to workers: {chunk_ids}")

        response = client.notify_workers(
            Subject=message['Subject'],
            MessageText=message['MessageText'],
            WorkerIds=chunk_ids
        ) 

        for failure in response['NotifyWorkersFailureStatuses']:
            logger.warn(f"Notification failed for {failure.pop('WorkerId')}: {failure}")

    logger.info('Finished sending notifications.')