"""Utilities for interacting with MTurk."""

import logging
import os
import boto3
from botocore.config import Config

from typing import Optional

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
    config = Config(retries={'max_attempts': settings.MAX_ATTEMPTS})
    client = session.client(
        service_name='mturk',
        region_name=region_name,
        endpoint_url=endpoint_url,
        config=config
    )

    return client


def get_qual_by_name(client: boto3.client, qual_name: str) -> Optional[dict]:
    """Find qual by name.

    Search MTurk qualifications for qual with qual_name. Return if found in
    first 100 results.

    NOTE: Only searches quals created/owned by the user's MTurk account.

    Parameters
    ----------
    client : boto3.client
        Boto3 MTurk client.
    qual_name : str
        Name of qualification to search for.

    Returns
    -------
    dict or None
        If qual found, return Dict with qual info.
        Else, return None.

    """
    response = client.list_qualification_types(
        Query=qual_name,
        MustBeRequestable=True,
        MustBeOwnedByCaller=True,
        MaxResults=100
    )
    for qual in response['QualificationTypes']:
        name = qual.pop('Name')
        if name == qual_name:
            return qual.pop('QualificationTypeId')
