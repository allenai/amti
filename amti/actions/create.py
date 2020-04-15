"""Functions for creating HITs"""

import json
import logging
import os
import shutil
import tempfile
import uuid

import jinja2

from amti import settings
from amti import utils


logger = logging.getLogger(__name__)


def initialize_batch_directory(
        definition_dir,
        data_path,
        save_dir):
    """Create a directory on disk that represents a batch.

    Create a directory on disk which brings together the basic elements
    of a batch, i.e. files defining a HIT template and a JSON lines file
    providing data with which to populate the template. This batch
    directory can then be used to upload a batch of HITs in MTurk.

    To simultaneously create the batch directory and upload the HITs to
    MTurk, use the ``create_batch`` function.

    Parameters
    ----------
    definition_dir : str
        the path to the definition directory.
    data_path : str
        the path to a JSONL file holding the data that should be used to
        generate the HITs in the batch.
    save_dir : str
        the path to the directory in which to write the batch
        directory.

    Returns
    -------
    batch_dir : str
        the path to the batch directory.
    """
    # construct important paths
    batch_dir_name, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    readme_file_name, _ = batch_dir_subpaths['readme']
    commit_file_name, _ = batch_dir_subpaths['commit']
    batchid_file_name, _ = batch_dir_subpaths['batchid']
    data_file_name, _ = batch_dir_subpaths['data']
    definition_dir_name, definition_dir_subpaths = \
        batch_dir_subpaths['definition']

    hittype_properties_path = os.path.join(
        definition_dir,
        definition_dir_subpaths['hittype_properties'][0])
    hit_properties_path = os.path.join(
        definition_dir,
        definition_dir_subpaths['hit_properties'][0])

    # create a UUID for the batch and the path to the batch dir
    batch_id = str(uuid.uuid4())
    batch_dir = os.path.join(
        save_dir, batch_dir_name.format(batch_id=batch_id))

    # use a temporary working directory to build up the batch directory
    with tempfile.TemporaryDirectory() as working_dir:
        # write the README file
        readme_path = os.path.join(working_dir, readme_file_name)
        with open(readme_path, 'w') as readme_file:
            readme_file.write(settings.BATCH_README)

        # write the COMMIT file
        current_commit = utils.log.get_current_commit() or '<none>'
        commit_path = os.path.join(working_dir, commit_file_name)
        with open(commit_path, 'w') as commit_file:
            commit_file.write(current_commit)

        # write the BATCHID file
        batchid_path = os.path.join(working_dir, batchid_file_name)
        with open(batchid_path, 'w') as batchid_file:
            batchid_file.write(batch_id)

        # validate the definition data
        with open(hittype_properties_path, 'r') as hittype_properties_file:
            hittype_properties = json.load(hittype_properties_file)
        hittype_validation_errors = utils.validation.validate_dict(
            hittype_properties, settings.HITTYPE_PROPERTIES)
        if hittype_validation_errors:
            raise ValueError(
                'HIT Type properties file ({hittype_properties_path})'
                ' had the following validation errors:'
                '\n{validation_errors}'.format(
                    hittype_properties_path=hittype_properties_path,
                    validation_errors='\n'.join(hittype_validation_errors)))

        with open(hit_properties_path, 'r') as hit_properties_file:
            hit_properties = json.load(hit_properties_file)
        hit_validation_errors = utils.validation.validate_dict(
            hit_properties, settings.HIT_PROPERTIES)
        if hit_validation_errors:
            raise ValueError(
                'HIT properties file ({hit_properties_path})'
                ' had the following validation errors:'
                '\n{validation_errors}'.format(
                    hit_properties_path=hit_properties_path,
                    validation_errors='\n'.join(hit_validation_errors)))

        # copy the definition data to the working directory
        working_definition_dir = os.path.join(
            working_dir, definition_dir_name)
        os.mkdir(working_definition_dir)
        for _, (file_name, _) in definition_dir_subpaths.items():
            shutil.copyfile(
                os.path.join(definition_dir, file_name),
                os.path.join(working_definition_dir, file_name))

        # validate the batch data (data.jsonl)
        with open(data_path, 'r') as data_file:
            for i, ln in enumerate(data_file):
                try:
                    json.loads(ln.rstrip())
                except ValueError:
                    raise ValueError(
                        f'Line {i+1} of {data_path} did not validate as'
                        f' JSON. Please make sure file is in JSON Lines'
                        f' format.')

        # copy the batch data (data.jsonl) to the working directory
        working_data_path = os.path.join(working_dir, data_file_name)
        shutil.copyfile(data_path, working_data_path)

        # copy the working_dir to the correct location
        shutil.copytree(working_dir, batch_dir)

    return batch_dir


def estimate_batch_cost(definition_dir, data_path):
    """
    Estimate the cost of a batch.

    This function takes ``definition_dir`` and ``data_path`` strings and then
    estimates the cost of a batch created with them. Since this function takes
    the defintion directory and data file, it can estimate the cost of a batch
    either before or after it's created.

    Parameters
    ----------
    definition_dir : str
        the path to the batch's definition directory.
    data_path : str
        the path to the batch's data file.

    Returns
    -------
    float
        the estimated cost of uploading this batch to MTURK (in USD),
        including MTURK overhead.
    """
    # construct all necessary paths
    _, definition_dir_subpaths = settings.BATCH_DIR_STRUCTURE[1]['definition']
    hittype_properties_file_name, _ = \
        definition_dir_subpaths['hittype_properties']
    hit_properties_file_name, _ = definition_dir_subpaths['hit_properties']

    hittype_properties_path = os.path.join(
        definition_dir,
        hittype_properties_file_name)
    hit_properties_path = os.path.join(
        definition_dir,
        hit_properties_file_name)

    # Load relevant files

    with open(hittype_properties_path, 'r') as hittype_properties_file:
        hittype_properties = json.load(hittype_properties_file)

    with open(hit_properties_path, 'r') as hit_properties_file:
        hit_properties = json.load(hit_properties_file)

    with open(data_path, "r") as data_file:
        n_hits = sum(1 for ln in data_file if ln.strip() != '')

    # Estimate cost

    estimated_cost = float(hittype_properties["Reward"]) \
        * int(hit_properties["MaxAssignments"]) \
        * n_hits \
        * settings.TURK_OVERHEAD_FACTOR

    return estimated_cost


def upload_batch(
        client,
        batch_dir):
    """Upload a batch to MTurk.

    Upload a batch to MTurk by creating HITs for it. To create a batch,
    use the ``initialize_batch_directory`` function.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    batch_dir : str
        the path to the batch directory.

    Returns
    -------
    hittype_id : str
        the HIT Type ID for the HIT Type created for the batch.
    hit_ids : List[str]
        the HIT IDs for the newly created HITs.
    """
    # construct all necessary paths
    _, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    definition_dir_name, definition_dir_subpaths = \
        batch_dir_subpaths['definition']
    batchid_file_name, _ = batch_dir_subpaths['batchid']
    question_template_file_name, _ = \
        definition_dir_subpaths['question_template']
    hittype_properties_file_name, _ = \
        definition_dir_subpaths['hittype_properties']
    hit_properties_file_name, _ = definition_dir_subpaths['hit_properties']
    data_file_name, _ = batch_dir_subpaths['data']

    batchid_path = os.path.join(
        batch_dir, batchid_file_name)
    question_template_path = os.path.join(
        batch_dir,
        definition_dir_name,
        question_template_file_name)
    hittype_properties_path = os.path.join(
        batch_dir,
        definition_dir_name,
        hittype_properties_file_name)
    hit_properties_path = os.path.join(
        batch_dir,
        definition_dir_name,
        hit_properties_file_name)
    data_path = os.path.join(
        batch_dir, data_file_name)

    # load relevant data
    with open(batchid_path, 'r') as batchid_file:
        batch_id = batchid_file.read().rstrip()

    with open(question_template_path, 'r') as question_template_file:
        question_template = jinja2.Template(question_template_file.read())

    with open(hittype_properties_path, 'r') as hittype_properties_file:
        hittype_properties = json.load(hittype_properties_file)

    with open(hit_properties_path, 'r') as hit_properties_file:
        hit_properties = json.load(hit_properties_file)

    logger.debug(f'Creating HIT Type with properties: {hittype_properties}')

    hittype_response = client.create_hit_type(**hittype_properties)
    hittype_id = hittype_response['HITTypeId']

    logger.debug(f'New HIT Type (ID: {hittype_id}) created.')

    hit_ids = []
    with open(data_path, 'r') as data_file:
        for i, ln in enumerate(data_file):
            if ln.strip() == '':
                logger.warning(f'Line {i+1} in {data_path} is empty. Skipping.')
                continue
            else:
                logger.debug(f'Creating HIT {i+1} using data: {ln}')

            ln_data = json.loads(ln.rstrip())
            question = question_template.render(**ln_data)
            requester_annotation = f'batch={batch_id}'
            hit_response = client.create_hit_with_hit_type(
                HITTypeId=hittype_id,
                Question=question,
                RequesterAnnotation=requester_annotation,
                **hit_properties)
            hit_id = hit_response['HIT']['HITId']
            logger.debug(f'Created New HIT (ID: {hit_id}).')
            hit_ids.append(hit_id)

    ids = {
        'hittype_id': hittype_id,
        'hit_ids': hit_ids
    }

    incomplete_file_path = os.path.join(
        batch_dir, settings.INCOMPLETE_FILE_NAME)
    with open(incomplete_file_path, 'w') as incomplete_file:
        json.dump(ids, incomplete_file)

    logger.info(f'Created {i+1} HITs.')

    return ids


def create_batch(
        client,
        definition_dir,
        data_path,
        save_dir):
    """Create a batch, writing it to disk and uploading it to MTurk.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    definition_dir : str
        the path to the definition directory.
    data_path : str
        the path to a JSONL file holding the data that should be used to
        generate the HITs in the batch.
    save_dir : str
        the path to the directory in which to write the batch directory.

    Returns
    -------
    str
        the path to the batch directory.
    """
    logger.info('Writing batch.')

    batch_dir = initialize_batch_directory(
        definition_dir=definition_dir,
        data_path=data_path,
        save_dir=save_dir)

    logger.info('Uploading batch to MTurk.')

    ids = upload_batch(client=client, batch_dir=batch_dir)

    logger.info('HIT Creation Complete.')

    return batch_dir


def create_qualificationtype(
        client,
        definition_dir,
        save_dir):
    """Create a qualification type in MTurk.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    definition_dir : str
        the path to the directory defining the qualification type.
    save_dir : str
        the path to the directory in which to write the qualification
        type directory.

    Returns
    -------
    None
    """
    logger.info('Creating qualification type directory.')

    qualificationtype_dir_name, qualificationtype_dir_subpaths = \
        settings.QUALIFICATIONTYPE_DIR_STRUCTURE
    definition_dir_name, definition_dir_subpaths = \
        qualificationtype_dir_subpaths['definition']
    properties_file_name, _ = definition_dir_subpaths['properties']
    test_file_name, _ = definition_dir_subpaths['test']
    answerkey_file_name, _ = definition_dir_subpaths['answerkey']
    qualificationtype_file_name, _ = \
        qualificationtype_dir_subpaths['qualificationtype']

    # construct useful paths
    properties_path = os.path.join(
        definition_dir, properties_file_name)
    test_path = os.path.join(
        definition_dir, test_file_name)
    answerkey_path = os.path.join(
        definition_dir, answerkey_file_name)

    # read in and validate the qualification type properties
    with open(properties_path, 'r') as properties_file:
        properties = json.load(properties_file)
    properties_validation_errors = utils.validation.validate_dict(
        properties, settings.QUALIFICATIONTYPE_PROPERTIES)
    if properties_validation_errors:
        raise ValueError(
            'Qualification Type properties file ({properties_path}) had'
            ' the following validation errors:'
            '\n{validation_errors}'.format(
                properties_path=properties_path,
                validation_errors='\n'.join(properties_validation_errors)))

    # read in the qualification test
    if os.path.exists(test_path):
        with open(test_path, 'r') as test_file:
            properties['Test'] = test_file.read()

    # read in the answerkey
    if os.path.exists(answerkey_path):
        with open(answerkey_path, 'r') as answerkey_file:
            properties['AnswerKey'] = answerkey_file.read()

    with tempfile.TemporaryDirectory() as working_dir:
        # construct output paths
        working_definition_dir = os.path.join(
            working_dir, definition_dir_name)
        os.mkdir(working_definition_dir)

        # copy the definition files over
        for _, (file_name, _) in definition_dir_subpaths.items():
            original_path = os.path.join(definition_dir, file_name)
            new_path = os.path.join(working_definition_dir, file_name)
            if (file_name not in [test_file_name, answerkey_file_name]
                or os.path.exists(original_path)):
                shutil.copyfile(original_path, new_path)

        # create the qualification type
        qualificationtype_response = client.create_qualification_type(**properties)
        qualificationtype_id = \
            qualificationtype_response['QualificationType']['QualificationTypeId']

        qualificationtype_path = os.path.join(
            working_dir, qualificationtype_file_name.format(
                qualificationtype_id=qualificationtype_id))
        with open(qualificationtype_path, 'w') as qualificationtype_file:
            json.dump(
                qualificationtype_response,
                qualificationtype_file,
                default=utils.serialization.json_helper)

        shutil.copytree(
            working_dir,
            os.path.join(
                save_dir,
                qualificationtype_dir_name.format(
                    qualificationtype_id=qualificationtype_id)))

    logger.info(
        f'Created Qualification Type (ID: {qualificationtype_id}).')
