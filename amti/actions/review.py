"""Functions for reviewing HITs"""

import json
import logging
import os
from xml.dom import minidom

from amti import settings


logger = logging.getLogger(__name__)


def review_hit(
        client,
        hit_id,
        approve_all):
    """Manually review the results from a HIT.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    hit_id : str
        the ID for the HIT to approve or reject.
    approve_all : bool
        a flag to decide approve all submissions

    Returns
    -------
    None.
    """
    logger.debug(f'Fetching HIT (ID: {hit_id}).')

    hit = client.get_hit(HITId=hit_id)
    hit_status = hit['HIT']['HITStatus']
    if hit_status != 'Reviewable':
        logger.info(
            f'HIT (ID: {hit_id}) has status "{hit_status}" and is not'
            f' "Reviewable". Skipping.')
        return

    logger.info(f'HIT {hit_id} Status: {hit_status}')

    assignments_paginator = client.get_paginator(
        'list_assignments_for_hit')
    assignments_pages = assignments_paginator.paginate(HITId=hit_id)
    for i, assignments_page in enumerate(assignments_pages):
        logger.debug(f'Reviewing assignments. Page {i}.')
        for assignment in assignments_page['Assignments']:
            assignment_id = assignment['AssignmentId']
            assignment_status = assignment['AssignmentStatus']
            answers_xml = minidom.parseString(assignment['Answer'])

            logger.info(
                f'Assignment (ID: {assignment_id}) Status: {assignment_status}.')

            if assignment_status != 'Submitted':
                logger.debug(
                    f'Assignment (ID: {assignment_id}) does not have status'
                    f' "Submitted". Skipping.')
                continue
            elif assignment_status == 'Submitted':
                if approve_all:
                    logger.info(f'Approving assignment (ID: {assignment_id}).')
                    client.approve_assignment(
                        AssignmentId=assignment_id,
                        OverrideRejection=False)
                else:
                    logger.info(f'Reviewing assignment (ID: {assignment_id}).')

                    print(
                        'HIT ID: {hit_id}'
                        '\nAssignment ID: {assignment_id}'
                        '\n'
                        '\nAnswers'
                        '\n======='
                        '\n{answers}'.format(
                            hit_id=hit_id,
                            assignment_id=assignment_id,
                            answers=answers_xml.toprettyxml()))

                    approve = None
                    while approve is None:
                        user_input = input('Approve? [y/n]').strip().lower()
                        if user_input in ['y', 'n']:
                            approve = user_input == 'y'
                        else:
                            print('Please type either "y" or "n".')

                    if approve:
                        logger.info(f'Approving assignment (ID: {assignment_id}).')
                        client.approve_assignment(
                            AssignmentId=assignment_id,
                            OverrideRejection=False)
                    else:
                        logger.info(
                            f'Did not approve assignment (ID: {assignment_id}).'
                            f' Please make sure to manually reject it.')


def review_batch(
        client,
        batch_dir,
        approve_all):
    """Manually review the HITs in a batch.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    batch_dir : str
        the path to the directory for the batch.
    approve_all : bool
        a flag to decide approve all submissions

    Returns
    -------
    None.
    """
    batch_dir_name, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    batchid_file_name, _ = batch_dir_subpaths['batchid']
    incomplete_file_name = settings.INCOMPLETE_FILE_NAME

    batchid_file_path = os.path.join(
        batch_dir, batchid_file_name)
    incomplete_file_path = os.path.join(
        batch_dir, settings.INCOMPLETE_FILE_NAME)

    with open(batchid_file_path) as batchid_file:
        batch_id = batchid_file.read().strip()

    if not os.path.isfile(incomplete_file_path):
        raise ValueError(
            f'No {incomplete_file_name} file was found in {batch_dir}.'
            f' Please make sure that the directory is a batch that has'
            f' HITs waiting for review.')
    with open(incomplete_file_path) as incomplete_file:
        hit_ids = json.load(incomplete_file)['hit_ids']

    logger.info(f'Reviewing batch {batch_id}.')

    for hit_id in hit_ids:
        review_hit(client=client, hit_id=hit_id, approve_all=approve_all)

    logger.info(f'Review of batch {batch_id} is complete.')
