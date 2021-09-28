"""Command line interface for listing associated Workers with quals"""

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
@click.option(
    '--qual', '-q', 
    help='QualificationId (or name, if --name flag passed).')
@click.option(
    '--status', '-s',
    help='The status of the Qualifications to return. Can be `Granted` or `Revoked`.')
@click.option(
    '--live', '-l',
    is_flag=True,
    help='View the status of HITs from the live MTurk site.')
def associated(qual, status, live):
    """List all the Workers that have been associated with a given Qualification type.

    NOTE: Only works with quals that both exist and are owned by the user.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)
    logger.info(f'Listing all the workers associated with {qual} (status: {status}) . . . ')

    response = client.list_workers_with_qualification_type(
        QualificationTypeId=qual,
        Status=status
    )
    if response['NumResults'] == 0:
        logger.info("No one is associated! ")
    else:
        logger.info("List of workers: ")
        for w in response['Qualifications']:
            logger.info(f" -> WorkerId: {w['WorkerId']} - granted-time: {w['GrantTime']}")

    logger.info('Finished listing the workers.')