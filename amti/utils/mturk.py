"""Utilities for interacting with MTurk."""

import logging

import boto3

from amti import settings


logger = logging.getLogger(__name__)


def get_mturk_client(env):
    """Return a client for Mechanical Turk.

    Return a client for Mechanical Turk that is configured for ``env``,
    the environment in which we'd like to run.

    Parameters
    ----------
    env : str
        The environment to get a client for. The value of ``env`` should
        be one of the supported environments.

    Returns
    -------
    MTurk.Client
        A boto3 client for Mechanical Turk configured for ``env``.
    """
    region_name = settings.ENVS[env]['region_name']
    endpoint_url = settings.ENVS[env]['endpoint_url']

    logger.debug(
        f'Creating mturk client in region {region_name} with endpoint'
        f' {endpoint_url}.')
    client = boto3.client(
        service_name='mturk',
        region_name=region_name,
        endpoint_url=endpoint_url)

    return client
