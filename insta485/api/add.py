"""
Insta485 POST api.

URLs include:
/api/v1/comments/?postid=<postid>
/api/v1/likes/?postid=<postid>

"""
import flask

import insta485
from insta485.api.helper import check_authorization


@insta485.app.route("/api/v1/comments/", methods=['POST'])
def post_comment():
    """Comment a post."""
    logname = check_authorization()

    # create a new comment
    postid = flask.request.args.get("postid")
    text = flask.request.json.get("text", None)
    if not text:
        return flask.jsonify({}), 400

    connection = insta485.model.get_db()
    # delete from database
    connection.execute(
        "INSERT INTO comments (owner, postid, text) VALUES (?,?,?)",
        (logname, postid, text)
    )

    # get new data from existing connection
    commentid = connection.execute("SELECT last_insert_rowid()").fetchone()
    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": "/users/" + logname + "/",
        "text": text,
        "url": "/api/v1/comments/" + str(commentid) + "/"
    }
    # context.append(words)
    return flask.jsonify(**context), 201


@insta485.app.route("/api/v1/likes/", methods=['POST'])
def post_like():
    """Like a post."""
    logname = check_authorization()

    postid = flask.request.args.get("postid")

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT likeid FROM likes WHERE owner = ? AND postid = ?",
        (logname, postid)
    ).fetchone()

    # if already liked
    if cur:
        likeid = cur['likeid']
        context = {
            "likeid": likeid,
            "url": "/api/v1/likes/" + str(likeid) + "/"
        }
        return flask.jsonify(**context), 200

    # add like
    cur = connection.execute(
        "INSERT INTO likes (owner, postid) VALUES (?,?)",
        (logname, postid)
    )

    # get likeid and return
    likeid = connection.execute(
        "SELECT last_insert_rowid()"
    ).fetchone()
    context = {
        "likeid": likeid,
        "url": "/api/v1/likes/" + str(likeid) + "/"
    }
    return flask.jsonify(**context), 201
