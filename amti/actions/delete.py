"""Functions for deleting HITs from MTurk"""

import json
import logging
import os

from amti import settings


logger = logging.getLogger(__name__)


def delete_hit(
        client,
        hit_id):
    """Delete the HIT corresponding to ``hit_id`` from MTurk.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    hit_id : str
        the ID for the HIT to delete.

    Returns
    -------
    None.
    """
    logger.debug(f'Deleting HIT (ID: {hit_id}).')

    client.delete_hit(HITId=hit_id)

    logger.debug(f'HIT (ID: {hit_id}) deleted.')


def delete_batch(
        client,
        batch_dir):
    """Delete the batch of HITs represented by ``batch_dir`` from MTurk.

    Only batches that have their results collected can be deleted.

    Parameters
    ----------
    client : MTurk.Client
        a boto3 client for MTurk.
    batch_dir : str
        the path to the batch directory.

    Returns
    -------
    None.
    """
    batch_dir_name, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    batchid_file_name, _ = batch_dir_subpaths['batchid']
    results_dir_name, results_dir_subpaths = batch_dir_subpaths['results']
    hit_dir_name, hit_dir_subpaths = results_dir_subpaths['hit_dir']
    hit_file_name, _ = hit_dir_subpaths['hit']

    batchid_file_path = os.path.join(
        batch_dir, batchid_file_name)
    results_dir = os.path.join(batch_dir, results_dir_name)

    with open(batchid_file_path) as batchid_file:
        batch_id = batchid_file.read().strip()

    logger.info(f'Deleting batch {batch_id}.')

    for dir_path, dir_names, file_names in os.walk(results_dir):
        if hit_file_name in file_names:
            # read the HIT ID from the HIT's file
            hit_file_path = os.path.join(dir_path, hit_file_name)
            with open(hit_file_path, 'r') as hit_file:
                hit_id = json.load(hit_file)['HIT']['HITId']

            logger.debug(f'Deleting HIT (ID: {hit_id}).')

            client.delete_hit(HITId=hit_id)
