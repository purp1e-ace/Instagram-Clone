"""
Insta485 index (main) view.

URLs include:
/
"""

import uuid
import pathlib
import flask


def check_logged_in():
    """Already logged in."""
    if 'username' not in flask.session:
        return True
    return False


def get_logname():
    """Get logname."""
    return flask.session['username']


def get_uuidbasename(filename):
    """Get UUIDBASENAME."""
    stem = uuid.uuid4().hex
    suffix = pathlib.Path(filename).suffix.lower()
    uuid_basename = f"{stem}{suffix}"
    return uuid_basename
