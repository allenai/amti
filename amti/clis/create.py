"""Command line interfaces for creating HITs"""

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

    For an example, see
    `here <https://github.com/allenai/amti/tree/master/examples/external-question/definition`.

    DATA_PATH should be a `JSON Lines <http://jsonlines.org/>`_
    file. For an example, see
    `here <https://github.com/allenai/amti/tree/master/examples/external-question/data.jsonl>`.

    SAVE_DIR should be a path to a directory in which the batch's data
    will be saved.
    """
    env = 'live' if live else 'sandbox'

    worker_url = settings.ENVS[env]['worker_url']

    client = utils.mturk.get_mturk_client(env)

    batch_dir = actions.create.create_batch(
        client=client,
        definition_dir=definition_dir,
        data_path=data_path,
        save_dir=save_dir)

    logger.info(
        f'Finished creating batch directory: {batch_dir}.'
        f'\n'
        f'\n    Preview HITs: {worker_url}'
        f'\n')


@click.command(
    context_settings={
        'help_option_names': ['--help', '-h']
    })
@click.argument(
    'definition_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument(
    'save_dir',
    type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    '--live', '-l',
    is_flag=True,
    help='Create the Qualification Type on the live MTurk site.')
def create_qualificationtype(definition_dir, save_dir, live):
    """Create a Qualification Type using DEFINITION_DIR.

    Create a Qualification Type using DEFINITION_DIR, and then save
    that Qualification Type's defining data to SAVE_DIR.

    DEFINITION_DIR should be a directory containing files with the
    following names:

      \b
      - qualificationtypeproperties.json: the defining properties for
        the qualication type.
      - test.xml: the XML defining the qualification test for the
        qualification type.
      - answerkey.xml: the answer key for the qualification test.

    For an example, see
    `here <https://github.com/allenai/amti/tree/master/examples/qualification-type/definition>`.

    SAVE_DIR should be a path to a directory in which the qualification
    type's data will be saved.
    """
    env = 'live' if live else 'sandbox'

    requester_url = settings.ENVS[env]['requester_url']

    client = utils.mturk.get_mturk_client(env)

    actions.create.create_qualificationtype(
        client=client,
        definition_dir=definition_dir,
        save_dir=save_dir)

    logger.info(
        f'Finished.'
        f'\n'
        f'\n    View the Qualification Type: {requester_url}'
        f'\n')
