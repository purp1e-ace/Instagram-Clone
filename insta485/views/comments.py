"""
Insta485 index (main) view.

URLs include:
/
"""
import flask
from flask import abort
import insta485
from insta485.views.helper import check_logged_in
from insta485.views.helper import get_logname


@insta485.app.route('/comments/', methods=['POST'])
def comment_post():
    """Comment a post."""
    check_logged_in()
    logname = get_logname()
    operation = flask.request.form['operation']

    # set redirect target
    target = flask.request.args.get('target')
    if target is None:
        target = flask.url_for('show_index')

    connection = insta485.model.get_db()

    # delete the comment
    if operation == 'delete':
        commentid = flask.request.form['commentid']
        # check accessibility of the comment
        cur = connection.execute(
            "SELECT * FROM comments WHERE commentid = ?",
            (commentid,)
        )
        if cur.fetchone()['owner'] != logname:
            abort(403)

        # update the database
        connection.execute(
            "DELETE FROM comments WHERE commentid =?",
            (commentid,)
        )
    # create a new comment
    if operation == 'create':
        postid = flask.request.form['postid']
        text = flask.request.form['text']
        # check if context is empty
        if text == '':
            abort(400)

        # delete from database
        connection.execute(
            "INSERT INTO comments (owner, postid, text) VALUES (?,?,?)",
            (logname, postid, text)
        )
    return flask.redirect(target)
