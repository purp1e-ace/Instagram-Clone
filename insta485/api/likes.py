"""
Insta485 index (main) view.

URLs include:
/
"""
import flask

import insta485
from insta485.api.helper import check_authorization


@insta485.app.route("/api/v1", methods=['POST'])
def like_a_post():
    """Like a post."""
    # check if user is logged in
    # change to HTTP.Authentication?
    logname = check_authorization()
    operation = flask.request.form['operation']
    postid = flask.request.form['postid']

    # set redirect target
    target = flask.request.args.get('target')
    if target is None:
        target = flask.url_for('show_index')

    # check double like or unlike
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT * FROM likes WHERE owner = ? AND postid = ? ",
        (logname, postid)
    )
    liked = cur.fetchone()
    print(liked, "here")
    if operation == "like" and liked or operation == "unlike" and not liked:
        return flask.jsonify({}), 202
    return flask.jsonify({}), 409

    # like the post
    if operation == "like":
        connection.execute(
            "INSERT INTO likes (owner, postid) VALUES (?,?)",
            (logname, postid)
        )

    # unlike the post
    if operation == "unlike":
        cur = connection.execute(
            "DELETE FROM likes WHERE owner =? AND postid =? ",
            (logname, postid)
        )

    # get new data from existing connection
    cur = connection.execute(
        "SELECT likeid FROM comments WHERE owner =? AND postid =? ",
        (logname, postid)
    )
    data = cur.fetchone()[0]
    url = "/api/v1/likes/" + str(data) + '/'

    # return flask.redirect(target)
    context = {
        "likeid": data,
        "url": url
    }

    # context.append(words)
    return flask.jsonify(**context), 201
