""" Module for worker management functions """
import boto3
import click
import csv
from typing import List

def chunk_list(items: List, n: int = 100) -> List:
    """Create generatator that yields n sized chunks of input list."""
    for i in range(0, len(items), n):
        yield items[i:i + n]

def read_workerids_from_file(file: click.Path) -> List:
    """Read WorkerIds from file.
    
    Read WorkerIds from CSV file. Return list of extracted WorkerIds.

    Parameters
    ----------
    file : click.Path
        Path to CSV file of WorkerIds.

    Returns
    -------
    list
        List of extracted WorkerId strings.
        
    """
    worker_ids = []
    with open(file, 'r') as f:
        reader = csv.reader(f)

        # check if first row is header
        first_row = next(reader)
        if 'WorkerId' not in first_row:
            worker_ids += first_row

        for row in reader:
            worker_ids += row

    return worker_ids