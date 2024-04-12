"""
REST API for delete.

URLs include:
/api/v1/likes/<likeid>/
/api/v1/comments/<commentid>/
"""

import flask

import insta485
from insta485.api.helper import check_authorization


@insta485.app.route('/api/v1/likes/<likeid>/', methods=['DELETE'])
def delete_like(likeid):
    """Delete one “like”. Return 204 on success."""
    connection = insta485.model.get_db()
    # check if like exists
    cur = connection.execute(
        "SELECT owner FROM likes WHERE likeid = ?",
        (likeid,)
    ).fetchone()
    if not cur:
        return flask.jsonify({}), 404

    # check if user has permission
    logname = check_authorization()
    if logname != cur['owner']:
        return flask.jsonify({}), 403

    # delete like
    connection.execute(
        "DELETE FROM likes WHERE likeid = ?",
        (likeid,)
    )

    return flask.jsonify({}), 204


@insta485.app.route('/api/v1/comments/<commentid>/', methods=['DELETE'])
def delete_comment(commentid):
    """Delete one comment. Return 204 on success."""
    connection = insta485.model.get_db()
    # check if like exists
    cur = connection.execute(
        "SELECT owner FROM comments WHERE commentid = ?",
        (commentid,)
    ).fetchone()
    if not cur:
        return flask.jsonify({}), 404

    # check if user has permission
    logname = check_authorization()
    if logname != cur['owner']:
        return flask.jsonify({}), 403

    # delete like
    connection.execute(
        "DELETE FROM comments WHERE commentid = ?",
        (commentid,)
    )

    return flask.jsonify({}), 204
