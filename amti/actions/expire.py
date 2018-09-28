"""Functions for expiring all (unanswered) HITs"""

import json
import logging
import os
import datetime

from amti import settings


logger = logging.getLogger(__name__)


def expire_batch(
        client,
        batch_dir):
    """Expire all the (unanswered) HITs in the batch.

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
            }

        where ``batch_id`` is the UUID for the batch.
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
            f' open HITs to be expired.')
    with open(incomplete_file_path) as incomplete_file:
        hit_ids = json.load(incomplete_file)['hit_ids']

    logger.info(f'Expiring HITs in batch {batch_id}.')

    for hit_id in hit_ids:
        hit = client.update_expiration_for_hit(
            HITId=hit_id,
            ExpireAt=datetime.datetime.now())

    logger.info(f'All HITs in batch {batch_id} are now expired.')

    return {
        'batch_id': batch_id
    }
