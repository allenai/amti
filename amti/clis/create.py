"""Command line interfaces for creating HITs"""

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
    'definition_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument(
    'data_path',
    type=click.Path(exists=True, file_okay=True, dir_okay=False))
@click.argument(
    'save_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--live', '-l',
    is_flag=True,
    help='Create HITs on the live MTurk site.')
def create_batch(definition_dir, data_path, save_dir, live):
    """Create a batch of HITs using DEFINITION_DIR and DATA_PATH.

    Create a batch of HITs using DEFINITION_DIR and DATA_PATH, and then
    save that batch's defining data to SAVE_DIR.

    DEFINITION_DIR should be a directory containing files with the
    following names:

      \b
      - NOTES: a text file with any notes about the definition, for
        example if a server must be run in order for the HIT to work
        then you could document that here.
      - question.xml.j2: a jinja2 template for an MTurk question xml
        file
      - hitproperties.json: a json file defining properties for the HITs
      - hittypeproperties.json: a json file defining properties for the
        HIT type that the newly created HITs will have.

    For an example, see 'TODO: INSERT LINK TO EXAMPLE HERE'.

    DATA_PATH should be a `JSON Lines <http://jsonlines.org/>`_
    file. For an example, see 'TODO: INSERT LINK TO EXAMPLE HERE'.

    SAVE_DIR should be a path to a directory in which the batch's data
    will be saved.
    """
    env = 'live' if live else 'sandbox'

    preview_url = settings.ENVS[env]['preview_url']

    client = mturk_utils.get_mturk_client(env)

    actions.create_batch(
        client=client,
        definition_dir=definition_dir,
        data_path=data_path,
        save_dir=save_dir)

    logger.info(
        f'Finished.'
        f'\n'
        f'\n    Preview HITs: {preview_url}'
        f'\n')
