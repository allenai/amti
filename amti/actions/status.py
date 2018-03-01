"""Functions for retrieving status information about HITs"""

import collections
import json
import logging
import os

from amti import settings


logger = logging.getLogger(__name__)


def status_batch(
        client,
        batch_dir):
    """Retrieve the status for a batch of HITs.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    batch_dir : str
        the path to the directory for the batch.

    Returns
    -------
    Dict[str, int]
        A dictionary mapping strings to integers. The dictionary will
        have the following form::

            {
                'batch_id': batch_id,
                'hit_count': hit_count,
                'hit_status_counts': hit_status_counts
            }

        where ``batch_id`` is the UUID for the batch, ``hit_count`` is a
        count of all the HITs in the batch and ``hit_status_counts`` is
        a dictionary counting the number of HITs with each of the
        different statuses.
    """
    # construct important paths
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

    logger.info(f'Retrieving status for batch {batch_id}.')

    hit_count = 0
    hit_status_counts = collections.defaultdict(int)
    for hit_id in hit_ids:
        hit = client.get_hit(HITId=hit_id)
        hit_count += 1
        hit_status_counts[hit['HIT']['HITStatus']] += 1

    logger.info(f'Retrieving status of batch {batch_id} is complete.')

    return {
        'batch_id': batch_id,
        'hit_count': hit_count,
        'hit_status_counts': hit_status_counts
    }
