"""Utilities for validating data"""


def validate_dict(dict_like, schema):
    """Return a list of validation error strings.

    Compare ``dict_like`` to ``schema``, returning a list of strings
    describing all the validation errors. In particular, validate that
    ``dict_like`` contains every key specified in ``schema`` as well as
    that each key's value is an instance of the type specified by
    ``schema``. It is *not* considered a validation error if
    ``dict_like`` has keys which are not in ``schema``.

    Parameters
    ----------
    dict_like : Dict
        a dictionary-like object to be validated against ``schema``.
    schema : Dict[String, type]
        a dictionary mapping strings to instances of ``type`` (i.e.,
        classes and built-in types like ``str``).

    Returns
    -------
    List[str]
        a list of strings describing all validation errors found when
        comparing ``dict_like`` to ``schema``.

    Example
    -------
    The following example shows a dictionary validated against a
    schema where the dictionary passes validation::

        >>> schema = {'foo': int}
        >>> data = {'foo': 3}
        >>> validate_dict(dict_like=data, schema=schema)
        []

    """
    validation_errors = []
    for key, value_type in schema.items():
        if key not in dict_like:
            validation_errors.append(f'Key ({key}) was not found.')
        elif not isinstance(dict_like[key], value_type):
            validation_errors.append(
                f'Key ({key}) is not of type {value_type}')

    return validation_errors
