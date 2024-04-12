"""
Insta485 index (main) view.

URLs include:
/
"""
import os
import uuid
import pathlib
import arrow
import flask
from flask import abort
import insta485
import insta485.api.helper
from insta485.views.helper import check_logged_in
from insta485.views.helper import get_logname


@insta485.app.route('/posts/<postid_url_slug>/', methods=['GET'])
def posts(postid_url_slug):
    """Display /posts/<postid_url_slug>/ route."""
    # check if user is logged in
    if check_logged_in():
        return flask.redirect("/accounts/login/")
    logname = get_logname()

    # Connect to database
    connection = insta485.model.get_db()

    current_post, comments, likes =\
        insta485.api.helper.get_post_by_id(postid_url_slug, connection)

    # humanize the timestamp
    current_post['created'] = arrow.get(
        current_post['created']).humanize()

    # check whether to show like or unlike button
    liked = False
    for like in likes:
        if like['owner'] == logname:
            liked = True

    # fetch the profile image
    cur = connection.execute(
        "SELECT * "
        "FROM users WHERE username = ?",
        (current_post['owner'],)
    )
    owner_image = cur.fetchone()
    # print("this is", owner_image)

    # Add database info to context
    context = {"logname": logname, "post": current_post,
               "comments": comments, "owner_image": owner_image['filename'],
               "likes": len(likes), "liked": liked}
    return flask.render_template("post.html", **context)


@insta485.app.route('/posts/', methods=['POST'])
def do_post():
    """Do a new post."""
    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']
    operation = flask.request.form['operation']

    # set redirect target
    target = flask.request.args.get('target')
    if target is None:
        target = flask.url_for('users', user_url_slug=logname)

    connection = insta485.model.get_db()

    # delete a post
    if operation == "delete":
        postid = flask.request.form['postid']
        # check accessibility of the post
        cur = connection.execute(
            "SELECT * FROM posts WHERE postid = ?",
            (postid,)
        )
        if cur.fetchone()['owner'] != logname:
            abort(403)

        # delete from database and delete the image file
        cur = connection.execute(
            "SELECT * FROM  posts WHERE postid = ?",
            (postid,)
        )
        filename = cur.fetchone()['filename']
        filepath = insta485.app.config['UPLOAD_FOLDER'] / filename
        os.remove(filepath)
        connection.execute(
            "DELETE FROM posts WHERE postid = ?",
            (postid,)
        )

    # create a new post
    if operation == "create":
        # Unpack flask object
        fileobj = flask.request.files["file"]
        filename = fileobj.filename

        # check if the file is empty
        if filename == "":
            abort(400)

        # Compute base name (filename without directory).  We use a UUID to
        # avoid clashes with existing files, and ensure that the name is
        # compatible with the filesystem. For best practive, we ensure
        # uniform file extensions (e.g. lowercase).
        stem = uuid.uuid4().hex
        suffix = pathlib.Path(filename).suffix.lower()
        uuid_basename = f"{stem}{suffix}"

        # Save to disk
        path = insta485.app.config["UPLOAD_FOLDER"] / uuid_basename
        fileobj.save(path)

        # update the database
        connection.execute(
            "INSERT INTO posts (filename, owner) VALUES (?,?)",
            (uuid_basename, logname)
        )

    return flask.redirect(target)
