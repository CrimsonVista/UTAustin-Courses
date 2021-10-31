import urllib.parse as urlparse

from django.core.exceptions import BadRequest

from urllib.parse import (
    quote as _quote, unquote as _unquote, urlencode as _urlencode,
)

def list_to_scope(scope):
    """Convert a list of scopes to a space separated string."""
    return " ".join([str(s) for s in scope])

def scope_to_list(scope):
    """Convert a space separated string to a list of scopes."""
    if isinstance(scope, (tuple, list, set)):
        return [str(s) for s in scope]
    elif scope is None:
        return None
    else:
        return scope.strip().split(" ")

def encode_params_utf8(params):
    """Ensures that all parameters in a list of 2-element tuples are encoded to
    bytestrings using UTF-8.
    """
    encoded = []
    for k, v in params:
        encoded.append((k.encode('utf-8'), v.encode('utf-8')))
    return encoded

def urlencode(params):
    utf8_params = encode_params_utf8(params)
    urlencoded = _urlencode(utf8_params)
    if isinstance(urlencoded, str):
        return urlencoded
    else:
        return urlencoded.decode("utf-8")

def add_params_to_qs(query, params):
    """Extend a query with a list of two-tuples."""
    if isinstance(params, dict):
        params = params.items()
    queryparams = urlparse.parse_qsl(query, keep_blank_values=True)
    queryparams.extend(params)
    return urlencode(queryparams)