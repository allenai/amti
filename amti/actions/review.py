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
    List of marked assignments.
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
    marked_assignments = []
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

                    input_string = """Would you like to (a)ccept, (r)eject, (s)kip or
                        (m)ark the assignment? [a/r/s/m]:"""
                    while True:
                        user_input = input(input_string).strip().lower()
                        if user_input in ['a', 'r', 's']:
                            break
                        elif user_input == 'm':
                            print('Assignment marked.')
                            while True:
                                user_input = input('Would you like to (a)ccept, (r)eject, or (s)kip this assignment?').strip().lower()
                                if user_input in ['a', 'r', 's']:
                                    break
                            marked_reason = input('Reason for marking? (Can be left blank.)').strip()
                            marked_assignments.append([assignment_id, user_input, marked_reason])
                        else:
                            print('Please type either "a", "r", "s", or "m".')

                    if user_input == 'a':  # accept
                        logger.info(f'Approving assignment (ID: {assignment_id}).')
                        client.approve_assignment(
                            AssignmentId=assignment_id,
                            OverrideRejection=False)
                    elif user_input == 'r':
                        while True:
                            user_input = input('Confirm rejection of this assignment [y/n]?').strip().lower()
                            if user_input  == 'y':
                                feedback = input('Assignment rejection feedback:').strip()
                                client.reject_assignment(
                                    AssignmentId=assignment_id,
                                    RequesterFeedback=feedback)
                            elif user_input == 'n':
                                break
                    else:
                        logger.info(f'Skipping assignment (ID: {assignment_id}).')


    return marked_assignments

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
    marked_file_path = os.path.join(
        batch_dir, 'marked_assignments.json')

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

    marked_assignments = []
    for hit_id in hit_ids:
        marked_assignments.extend(review_hit(client=client, hit_id=hit_id, approve_all=approve_all))

    if marked_assingments:
        with open(marked_file_path, 'w') as f:
            json.dump(data, f)

    logger.info(f'Review of batch {batch_id} is complete.')
