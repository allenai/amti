"""Command line interfaces for reviewing HITs"""

import logging

import boto3
import click

from amti import actions
from amti import settings
from amti.utils import mturk as mturk_utils


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
    help='Review HITs on the live MTurk site.')
def review_batch(batch_dir, live):
    """Review the batch of HITs defined in BATCH_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs with
    HITs out in MTurk and waiting for review, manually review each of
    the ready HITs at the command line.
    """
    env = 'live' if live else 'sandbox'

    client = mturk_utils.get_mturk_client(env)

    actions.review_batch(
        client=client,
        batch_dir=batch_dir)

    logger.info('Finished reviewing batch.')
