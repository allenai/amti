"""Command line interfaces for viewing the statuses of HITs"""

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
    help='View the status of HITs from the live MTurk site.')
def status_batch(batch_dir, live):
    """View the status of the batch of HITs defined in BATCH_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs with
    HITs out in MTurk and waiting for review or that have been reviewed,
    see that status of HITs in that batch.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    batch_status = actions.status.status_batch(
        client=client,
        batch_dir=batch_dir)

    batch_id = batch_status['batch_id']
    hit_count = str(batch_status['hit_count'])
    hit_status_counts = '\n    '.join(
        f'{status}: {count}'
        for status, count in batch_status['hit_status_counts'].items())

    print(
      f'\n'
        f'  Batch Status:'
      f'\n  ============='
      f'\n  Batch ID: {batch_id}'
      f'\n  HIT Count: {hit_count}'
      f'\n  HIT Status Counts:'
      f'\n    {hit_status_counts}'
      f'\n')

    logger.info('Finished retrieving batch status.')
