"""Helper functions."""
import flask

import insta485
from insta485.views.accounts import my_hash


def check_authorization():
    """Check if user is logged in."""
    authorized = False
    if flask.request.authorization is not None:
        username = flask.request.authorization['username']
        password = flask.request.authorization['password']
        authorized = password_is_correct(username, password)
    if not authorized and 'username' not in flask.session:
        raise InvalidUsage('Forbidden', status_code=403)
        # return flask.jsonify({}), 403
    return flask.session['username'] if \
        'username' in flask.session else username


# Implement an error handler.
# See https://flask.palletsprojects.com/en/1.1.x/patterns/apierrors/
class InvalidUsage(Exception):
    """This handles authenification errors somehow."""

    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        """Init."""
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        """Make dict."""
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@insta485.app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    """Handle invalid usage."""
    response = flask.jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def get_post_by_id(postid_url_slug, connection):
    """Get post by given id."""
    cur = connection.execute(
        "SELECT * "
        "FROM posts WHERE postid = ?",
        (postid_url_slug,)
    )

    # fetch the post
    current_post = cur.fetchone()
    if current_post is None:
        return flask.jsonify({}), 404

    # fetch the comments
    cur = connection.execute(
        "SELECT * "
        "FROM comments WHERE postid = ? "
        "ORDER BY commentid ASC",
        (postid_url_slug,)
    )
    comments = cur.fetchall()

    # fetch the who likes the post
    cur = connection.execute(
        "SELECT * "
        "FROM likes WHERE postid = ?",
        (postid_url_slug,)
    )
    likes = cur.fetchall()

    return current_post, comments, likes


def password_is_correct(username, password):
    """Check password."""
    # """Get the salt."""
    password_db_string = get_password(username)
    salt = password_db_string.split('$')[1]

    # """Hashing the password!!!"""
    hashed_password = my_hash(password, salt)

    return password_db_string == hashed_password


def get_password(username):
    """Get password helper function."""
    # """Helpfer function for getting a stored password"""

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT password "
        "FROM users "
        "WHERE username = ?",
        (username,)
    )

    # """Getting the hashed password in the database"""
    hashed_password = cur.fetchone()

    # """Checking if the username exists in the database"""

    if hashed_password is None:
        flask.jsonify({}), 403
    hashed_password = hashed_password['password']

    # """Getting the password."""
    return hashed_password
