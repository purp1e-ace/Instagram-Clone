"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import abort
import insta485


@insta485.app.route("/likes/", methods=['POST'])
def like_post():
    """Like a post."""
    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']
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
        abort(409)

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

    return flask.redirect(target)
