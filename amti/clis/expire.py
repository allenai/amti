"""Command line interfaces for expiring the HITs"""

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
    help='Expire the HITs from the live MTurk site.')
def expire_batch(batch_dir, live):
    """Expire all the HITs defined in BATCH_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs in MTurk,
    expire all the unanswered HITs.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    batch_expire = actions.expire.expire_batch(
        client=client,
        batch_dir=batch_dir)

    batch_id = batch_expire['batch_id']

    logger.info('Finished expiring batch.')
