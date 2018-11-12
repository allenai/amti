"""A function for extracting batch data into a tabular format."""

import csv
import html
import json
import logging
import os
from xml.dom import minidom

import click

from amti import settings
from amti import utils


logger = logging.getLogger(__name__)


TABULAR_SUPPORTED_FILE_FORMATS = [
    'csv',
    'json',
    'jsonl'
]
"""File formats supported by the ``tabular`` function."""
# Make sure to update the doc strings for
# ``amti.actions.extraction.tabular.tabular`` and
# ``amti.clis.extraction.tabular.tabular`` if you edit this constant.


def tabular(
        batch_dir,
        output_path,
        file_format):
    """Extract data in ``batch_dir`` to ``output_path`` as a table.

    Extract batch data into a tabular format; however, some metadata may
    not be copied over. Each assignment will become it's own row in the
    table with a separate column for each form field, as well as much of
    the assignment's metadata. The table will be written to
    ``output_path`` in the format specified by ``file_format``.

    Parameters
    ----------
    batch_dir : str
        the path to the batch's directory.
    output_path : str
        the path where the output file should be saved.
    file_format : str
        the file format to use when writing the data. Must be one of the
        supported file formats: csv (CSV), json (JSON), jsonl (JSON
        Lines).

    Returns
    -------
    None.
    """
    if file_format not in TABULAR_SUPPORTED_FILE_FORMATS:
        raise ValueError(
            'file_format must be one of {formats}.'.format(
                formats=', '.join(TABULAR_SUPPORTED_FILE_FORMATS)))

    # construct important paths
    _, batch_dir_subpaths = settings.BATCH_DIR_STRUCTURE
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
        f'Beginning to extract batch {batch_id} to tabular format.')

    rows = []
    for dir_path, dir_names, file_names in os.walk(results_dir):
        hit = None
        assignments = None
        for file_name in file_names:
            if file_name == hit_file_name:
                hit_path = os.path.join(dir_path, file_name)
                with open(hit_path, 'r') as hit_file:
                    hit = json.load(hit_file)
            elif file_name == assignments_file_name:
                assignments_path = os.path.join(
                    dir_path, assignments_file_name)
                with open(assignments_path, 'r') as assignments_file:
                    assignments = [
                        json.loads(ln.strip())
                        for ln in assignments_file
                    ]
            else:
                logger.warning(
                    f'Unexected file ({file_name}) located in'
                    f' {dir_path}')

        if hit is None or assignments is None:
            # if both ``hit`` and ``assignments`` are ``None``, then
            # this directory is simply not one we're interested in;
            # however, if exactly one is ``None`` then there's likely
            # been an error.
            if hit is None and assignments is not None:
                logger.warning(
                    f'Found assignments but no HIT in {dir_path}.')
            elif hit is not None and assignments is None:
                logger.warning(
                    f'Found HIT but no assignments in {dir_path}.')
            continue

        for assignment in assignments:
            row = {}

            # add relevant metadata from the HIT
            row['HITId'] = hit['HIT']['HITId']
            row['AssignmentDurationInSeconds'] =\
                hit['HIT']['AssignmentDurationInSeconds']
            row['AutoApprovalDelayInSeconds'] =\
                hit['HIT']['AutoApprovalDelayInSeconds']
            row['Expiration'] = hit['HIT']['Expiration']
            row['CreationTime'] = hit['HIT']['CreationTime']

            # add relevant metadata from the assignment
            row['AssignmentId'] = assignment['AssignmentId']
            row['WorkerId'] = assignment['WorkerId']
            row['AssignmentStatus'] = assignment['AssignmentStatus']
            row['AutoApprovalTime'] = assignment['AutoApprovalTime']
            row['AcceptTime'] = assignment['AcceptTime']
            row['SubmitTime'] = assignment['SubmitTime']
            row['ApprovalTime'] = assignment['ApprovalTime']

            # parse the response and add it to the row
            xml = minidom.parseString(assignment['Answer'])
            for answer_tag in xml.getElementsByTagName('Answer'):
                [question_identifier_tag] =\
                    answer_tag.getElementsByTagName(
                        'QuestionIdentifier')
                question_identifier = utils.xml.get_node_text(
                    question_identifier_tag)

                if question_identifier == 'doNotRedirect':
                    # some workers on Mechanical Turk modify their
                    # browser requests to send a 'doNotRedirect'
                    # field when posting results.
                    logger.warning(
                        f'Found a "doNotRedirect" field in'
                        f' {dir_path}. Dropping the field.')
                    continue

                [free_text_tag] = answer_tag.getElementsByTagName(
                    'FreeText')
                free_text = html.unescape(
                    utils.xml.get_node_text(free_text_tag))

                row[question_identifier] = free_text

            rows.append(row)

    with click.open_file(output_path, 'w') as output_file:
        if file_format == 'csv':
            csv_writer = csv.DictWriter(
                output_file,
                fieldnames=rows[0].keys())
            csv_writer.writeheader()
            csv_writer.writerows(rows)
        elif file_format == 'json':
            json.dump(rows, output_file)
        elif file_format == 'jsonl':
            output_file.write('\n'.join([
                json.dumps(row)
                for row in rows
            ]))
        else:
            raise NotImplementedError(
                f'Support for {file_format} has not been implemented.')

    logger.info(
        f'Finished extracting batch {batch_id} to tabular format.')
