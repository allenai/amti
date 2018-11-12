"""A function for extracting data from a batch as XML"""

import json
import logging
import os
import shutil
import tempfile
from xml.dom import minidom

from amti import settings


logger = logging.getLogger(__name__)


def xml(
        batch_dir,
        output_dir):
    """Extract the XML from assignments in a batch.

    Extract the XML from assignments in the batch represented by
    ``batch_dir`` and save the results to ``output_dir``. ``batch_dir``
    should be a batch that has all its HITs and assignments reviewed and
    downloaded. By default, the HITs and assignments are stored in a
    JSON lines format, so this function extracts the answer XML from the
    assignments into separate pretty-printed XML files for better
    consumption by humans and other systems.

    Parameters
    ----------
    batch_dir : str
        the path to the batch's directory.
    output_dir : str
        the path to the directory in which to save the output.

    Returns
    -------
    None.
    """
    # construct important paths
    batch_dir_name, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
    batchid_file_name, _ = batch_dir_subpaths['batchid']
    results_dir_name, results_dir_subpaths = batch_dir_subpaths['results']
    _, hit_dir_subpaths = results_dir_subpaths['hit_dir']
    hit_file_name, _ = hit_dir_subpaths['hit']
    assignments_file_name, _ = hit_dir_subpaths['assignments']

    batchid_file_path = os.path.join(
        batch_dir, batchid_file_name)
    results_dir = os.path.join(batch_dir, results_dir_name)

    with open(batchid_file_path) as batchid_file:
        batch_id = batchid_file.read().strip()

    logger.info(
        f'Beginning to extract batch {batch_id} to XML.')

    xml_dir_name = settings.XML_DIR_NAME_TEMPLATE.format(
        batch_id=batch_id)
    xml_dir_path = os.path.join(output_dir, xml_dir_name)
    with tempfile.TemporaryDirectory() as working_dir:
        for dir_path, dir_names, file_names in os.walk(results_dir):
            if hit_file_name in file_names:
                hit_dir_name = os.path.split(dir_path)[-1]
                hit_dir = os.path.join(working_dir, hit_dir_name)
                os.mkdir(hit_dir)

                assignments_path = os.path.join(
                    dir_path, assignments_file_name)
                with open(assignments_path, 'r') as assignments_file:
                    for ln in assignments_file:
                        assignment = json.loads(ln.rstrip())
                        assignment_id = assignment['AssignmentId']
                        xml = minidom.parseString(assignment['Answer'])

                        xml_file_name = settings.XML_FILE_NAME_TEMPLATE.format(
                            assignment_id=assignment_id)
                        xml_output_path = os.path.join(
                            hit_dir, xml_file_name)
                        with open(xml_output_path, 'w') as xml_output_file:
                            xml_output_file.write(
                                xml.toprettyxml(indent='  '))

        shutil.copytree(working_dir, xml_dir_path)

    logger.info(
        f'Finished extracting batch {batch_id} to XML.')
