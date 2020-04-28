"""Command line interfaces for reviewing HITs"""

import logging

import boto3
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
    help='Review HITs on the live MTurk site.')
@click.option(
    '--approve-all', '-a',
    is_flag=True,
    help="Approve all submissions.")
@click.option(
    '--mark-file-path', '-m',
    type=click.Path(
        exists=False,
        file_okay=True,
        dir_okay=False,
        writable=True,
        allow_dash=True),
    default='-',
    help='The path to the file in which to save the marked assignments.'
         ' Defaults to STDOUT.')
def review_batch(batch_dir, live, approve_all, mark_file_path):
    """Review the batch of HITs defined in BATCH_DIR.

    Given a directory (BATCH_DIR) that represents a batch of HITs with
    HITs out in MTurk and waiting for review, manually review each of
    the ready HITs at the command line.
    """
    env = 'live' if live else 'sandbox'

    client = utils.mturk.get_mturk_client(env)

    actions.review.review_batch(
        client=client,
        batch_dir=batch_dir,
        approve_all=approve_all,
        mark_file_path=mark_file_path)

    logger.info('Finished reviewing batch.')
