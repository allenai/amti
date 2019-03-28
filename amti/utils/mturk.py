"""Utilities for interacting with MTurk."""

import logging
import os

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

    profile = os.getenv('AWS_PROFILE')
    if profile is None:
        logger.debug('Creating mturk session with default environment/profile values.')
        session = boto3.session.Session()
    else:
        logger.debug(f'Creating mturk session with profile_name {profile}')
        session = boto3.session.Session(profile_name=profile)

    logger.debug(
        f'Creating mturk client in region {region_name} with endpoint'
        f' {endpoint_url}.')
    client = session.client(
        service_name='mturk',
        region_name=region_name,
        endpoint_url=endpoint_url)

    return client
