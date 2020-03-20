"""
amti.utils.logging
==================
Utilities for logging.
"""

import logging
import subprocess
import sys


LOG_FORMAT = '%(asctime)s:%(levelname)s:%(name)s:%(message)s'


def config_logging(log_level, file_path=None):
    """Configure python logging.

    Parameters
    ----------
    log_level : int
        the level to log at. Rather than passing an integer directly,
        you should import one of the log levels from the logging
        module, with ``logging.INFO`` and ``logging.DEBUG` being the
        most common.
    file_path : Optional[str]
        if a string is present, a file path at which the logging
        output should be written, otherwise ``None`` in which case
        logs will be written to STDOUT.

    Returns
    -------
    None.
    """
    # set logging on noisy dependencies
    logging.getLogger('boto').setLevel(logging.CRITICAL)
    logging.getLogger('botocore').setLevel(logging.CRITICAL)

    if file_path:
        logging.basicConfig(
            filename=file_path,
            filemode='a',
            format=LOG_FORMAT,
            level=log_level)
    else:
        logging.basicConfig(
            stream=sys.stdout,
            format=LOG_FORMAT,
            level=log_level)


def check_git_installed():
    """Return ``True`` if git is installed, otherwise return ``False``.

    Returns
    -------
    bool
        ``True`` if git is installed, ``False`` otherwise.
    """
    process = subprocess.run(
        ['git', '--version'],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL)

    return process.returncode == 0


def get_current_commit():
    """Return the current commit of the current directory.

    Return the current commit of the current directory. If the current
    directory is not a git repo or if git is not installed then return
    ``None``.

    Returns
    -------
    Optional[str]
        the full SHA for the commit of the current directory, or
        ``None`` if the current directory is not a git repo or git is
        not installed.
    """
    process = subprocess.run(
        ['git', 'rev-parse', '--verify', 'HEAD'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    git_installed = check_git_installed()

    if not git_installed:
        current_commit = None
    elif b'fatal: not a git repository' in process.stderr.lower():
        current_commit = None
    else:
        process.check_returncode()
        current_commit = process.stdout.decode('utf-8').rstrip()

    return current_commit


def is_repo_clean():
    """Return ``True`` if the repo has a clean working directory.

    Return ``True`` if the repo has a clean working directory, ``False``
    if it doesn't, and ``None`` if the current directory is not a git
    repo or git is not installed.

    Returns
    -------
    Optional[bool]
        ``True`` if the current working directory is a clean git repo,
        ``False`` if the current working directory is a dirty git repo,
        and ``None`` if the current working directory is not a git repo
        or if git is not installed.
    """
    process = subprocess.run(
        ['git', 'status', '--porcelain'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    git_installed = check_git_installed()

    if not git_installed:
        clean_repo = None
    elif b'fatal: not a git repository' in process.stderr.lower():
        clean_repo = None
    else:
        process.check_returncode()
        clean_repo = process.stdout.decode('utf-8') == ''

    return clean_repo


def log_current_commit(logger):
    """Log the current commit and whether the repo is clean.

    Log the current commit and whether the working directory for the
    repo is clean.

    Parameters
    ----------
    logger : logging.Logger
        the logger with which to log messages.

    Returns
    -------
    None.
    """
    current_commit = get_current_commit()
    clean_repo = is_repo_clean()

    if current_commit is None or clean_repo is None:
        logger.info(
            'Current directory does not appear to be a git repo.')
    else:
        status = 'clean' if clean_repo else 'dirty'
        logger.info(f'Current commit: {current_commit}')
        logger.info(f'Working directory status: {status}')
