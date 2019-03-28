""" Module for worker management functions """
import click
import csv
from typing import List

def create_batches(items: List, n=100) -> List:
    """ Create generator that splits items into batches of size n. """
    for i in range(0, len(items), n):
        yield items[i:i + n]

def read_workerids_from_file(file: click.Path) -> List:
    """ Read WorkerIds from file. Return list of extracted WorkerIds. """
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