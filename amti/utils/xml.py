"""Utilities for processing XML."""

from xml.dom import minidom


def get_node_text(node):
    """Return the text from a node that has only text as content.

    Calling this function on a node with multiple children or a non-text
    node child raises a ``ValueError``.

    Parameters
    ----------
    node : xml.dom.minidom.Node
        The node to extract text from.

    Returns
    -------
    str
        The text from node.
    """
    # handle the empty node case
    if len(node.childNodes) == 0:
        return ''

    # check error conditions
    if len(node.childNodes) > 1:
        raise ValueError(
            f'node ({node}) has multiple child nodes.')

    if not isinstance(node.childNodes[0], minidom.Text):
        raise ValueError(
            f"node's ({node}) child node is not a Text node.")

    # return the child node's text
    return node.childNodes[0].wholeText
