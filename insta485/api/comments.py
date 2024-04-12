"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
import insta485
from insta485.api.helper import check_authorization


@insta485.app.route('/api/v1/', methods=['POST'])
def comment_a_post(postid):
    """Comment a post."""
    logname = check_authorization()

    # create a new comment
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
    commentid = connection.execute("SELECT last_insert_rowid()")
    context = {
        "commentid": commentid,
        "lognameOwnsThis": True,
        "owner": logname,
        "ownerShowUrl": "/users/" + logname + "/",
        "text": text,
        "url": "/api/v1/comments/" + commentid + "/"
    }
    # context.append(words)
    return flask.jsonify(**context), 201
