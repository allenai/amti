"""Utilities for data serialization"""

import datetime


def json_helper(obj):
    """Help ``json.dump`` serialize objects to JSON.

    This function is written to be passed into ``json.dump`` as the
    argument to the ``default`` parameter, so that we can serialize a
    broader range of data types. Currently, this helper function can
    serialize ``datetime.date`` and ``datetime.datetime`` objects. If
    the object cannot be serialized, a ``TypeError`` is raised.

    Parameters
    ----------
    obj : object
        an object to be serialized.

    Returns
    -------
    str
        a string representing ``obj`` serialized as JSON.
    """
    if isinstance(obj, datetime.date):
        serialized_obj = obj.isoformat()
    elif isinstance(obj, datetime.datetime):
        serialized_obj = obj.isoformat()
    else:
        raise TypeError(f'Failed to serialize {obj}.')

    return serialized_obj
