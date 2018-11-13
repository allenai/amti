"""Functions for saving HITs to storage"""

import json
import logging
import os
import shutil
import tempfile

from amti import settings
from amti import utils


logger = logging.getLogger(__name__)


def save_batch(
        client,
        batch_dir):
    """Save results from turkers working a batch to disk.

    In order to save the results from a batch to disk, every HIT in the
    batch must be in a reviewable state.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    batch_dir : str
        the path to the batch's directory.

    Returns
    -------
    None.
    """
    # construct important paths
    batch_dir_name, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    batchid_file_name, _ = batch_dir_subpaths['batchid']
    results_dir_name, results_dir_subpaths = batch_dir_subpaths['results']
    hit_dir_name, hit_dir_subpaths = results_dir_subpaths['hit_dir']
    hit_file_name, _ = hit_dir_subpaths['hit']
    assignments_file_name, _ = hit_dir_subpaths['assignments']
    incomplete_file_name = settings.INCOMPLETE_FILE_NAME

    batchid_file_path = os.path.join(
        batch_dir, batchid_file_name)
    incomplete_file_path = os.path.join(
        batch_dir, settings.INCOMPLETE_FILE_NAME)
    results_dir = os.path.join(batch_dir, results_dir_name)

    with open(batchid_file_path) as batchid_file:
        batch_id = batchid_file.read().strip()

    if not os.path.isfile(incomplete_file_path):
        raise ValueError(
            f'No {incomplete_file_name} file was found in {batch_dir}.'
            f' Please make sure that the directory is a batch that has'
            f' HITs waiting for review.')
    with open(incomplete_file_path) as incomplete_file:
        hit_ids = json.load(incomplete_file)['hit_ids']

    logger.info(f'Retrieving HIT data for batch {batch_id}.')
    # construct the results in a temporary directory. Using a temporary
    # directory allows us to eagerly construct the results directory
    # without worrying about clean up in the event of an error
    # condition.
    with tempfile.TemporaryDirectory() as working_dir:
        for hit_id in hit_ids:
            hit_dir = os.path.join(
                working_dir,
                hit_dir_name.format(hit_id=hit_id))
            os.mkdir(hit_dir)

            hit_file_path = os.path.join(hit_dir, hit_file_name)
            assignments_file_path = os.path.join(
                hit_dir, assignments_file_name)

            logger.debug(f'Fetching HIT (ID: {hit_id}).')
            hit = client.get_hit(HITId=hit_id)

            logger.debug(f'Writing HIT (ID: {hit_id}) to {hit_file_path}.')
            with open(hit_file_path, 'w') as hit_file:
                json.dump(
                    hit,
                    hit_file, default=utils.serialization.json_helper)

            hit_status = hit['HIT']['HITStatus']
            if hit_status != 'Reviewable':
                raise ValueError(
                    f'HIT (ID: {hit_id}) has status "{hit_status}".'
                    f' In order to save a batch all HITs must have'
                    f' "Reviewable" status.')

            logger.debug(f'Fetching assignments for HIT (ID: {hit_id}).')
            assignments_paginator = client.get_paginator(
                'list_assignments_for_hit')
            assignments_pages = assignments_paginator.paginate(HITId=hit_id)
            with open(assignments_file_path, 'w') as assignments_file:
                for i, assignments_page in enumerate(assignments_pages):
                    logger.debug(f'Saving assignments. Page {i}.')
                    for assignment in assignments_page['Assignments']:
                        assignment_id = assignment['AssignmentId']
                        assignment_status = assignment['AssignmentStatus']

                        logger.debug(
                            f'Assignment (ID: {assignment_id}) Status:'
                            f' {assignment_status}.')

                        if assignment_status not in ['Approved', 'Rejected']:
                            raise ValueError(
                                f'Assignment (ID: {assignment_id}) has status'
                                f' "{assignment_status}". In order to save a'
                                f' batch all assignments must have "Approved"'
                                f' or "Rejected" status.')

                        assignments_file.write(
                            json.dumps(
                                assignment,
                                default=utils.serialization.json_helper
                            ) + '\n')

            logger.info(f'Finished saving HIT (ID: {hit_id}).')

        shutil.copytree(working_dir, results_dir)

    # remove the incomplete file since the batch is now complete
    os.remove(incomplete_file_path)

    logger.info(f'Saving batch {batch_id} is complete.')
