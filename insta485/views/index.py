"""
Insta485 index (main) view.

URLs include:
/
"""

import os
import arrow
import flask
from flask import abort
import insta485
import insta485.views.users
import insta485.views.follow_unfollow
import insta485.views.login
import insta485.views.posts
import insta485.views.accounts
from insta485.views.helper import check_logged_in


@insta485.app.route('/')
def show_index():
    """Index."""
    # check if user is logged in
    if check_logged_in():
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']

    # Connect to database
    connection = insta485.model.get_db()

    # Query database
    # fetch all posts
    cur = connection.execute(
        "SELECT * "
        "FROM posts post WHERE EXISTS "
        "(SELECT 1 FROM following follow "
        "WHERE follow.username1 = ? "
        "AND follow.username2 = post.owner) "
        "OR post.owner = ? ORDER BY postid DESC",
        (logname, logname)
    )
    posts = cur.fetchall()

    for post in posts:
        print("postid: ", post['postid'])

        # humanize timestamp
        post['created'] = arrow.get(post['created']).humanize()

        # fetch comments
        cur = connection.execute(
            "SELECT * "
            "FROM comments WHERE postid = ? "
            "ORDER BY commentid ASC",
            (post['postid'],)
        )
        post['comments'] = cur.fetchall()

        # fetch likes
        cur = connection.execute(
            "SELECT * "
            "FROM likes WHERE postid = ?",
            (post['postid'],)
        )
        post['likes'] = cur.fetchall()

        # check whether to show like or unlike button
        liked = False
        for like in post['likes']:
            if like['owner'] == logname:
                liked = True
        post['liked'] = liked
        post['likes'] = len(post['likes'])

        # fetch the profile image
        cur = connection.execute(
            "SELECT * "
            "FROM users WHERE username = ?",
            (post['owner'],)
        )
        post['owner_image'] = cur.fetchone()
        post['owner_image'] = post['owner_image']['filename']

    # Add database info to context
    context = {"logname": logname, "posts": posts}
    return flask.render_template("index.html", **context)


@insta485.app.route('/uploads/<filename>')
def uploads(filename):
    """Upload."""
    if 'username' not in flask.session:
        abort(403)
    if not os.path.exists(
            insta485.app.config['UPLOAD_FOLDER'] / filename):
        abort(404)
    return flask.send_from_directory(
        insta485.app.config['UPLOAD_FOLDER'], filename)
