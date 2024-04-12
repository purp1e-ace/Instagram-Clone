"""
Insta485 followers/following/explore pages.

URLs include:
/users/<user_url_slug>/followers/
/users/<user_url_slug>/following/
/explore/
"""
import flask
import insta485
from insta485.views.helper import check_logged_in


@insta485.app.route('/following/', methods=['POST'])
def follow_unfollow():
    """Follow/unfollow buttons."""
    username2 = flask.request.form.get('username')
    operation = flask.request.form.get('operation')
    target = flask.request.args.get('target')

    # check if user is logged in
    if check_logged_in():
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']

    if not target:
        return flask.redirect('/')

    connection = insta485.model.get_db()

    if operation == 'follow':
        cur = connection.execute("SELECT COUNT(*) FROM following "
                                 "WHERE username1 = ? AND username2 = ?",
                                 (logname, username2))
        if cur.fetchone() == 1:  # this relationship already exists
            flask.abort(409)
        # Connect to database
        connection = insta485.model.get_db()
        cur = connection.execute("INSERT INTO following "
                                 "(username1, username2) VALUES (?, ?)",
                                 (logname, username2))

    elif operation == 'unfollow':
        cur = connection.execute("SELECT COUNT(*) FROM following "
                                 "WHERE username1 = ? AND username2 = ?",
                                 (logname, username2))
        if cur.fetchone() == 0:
            # logname not following username already exists
            flask.abort(409)
        cur = connection.execute("DELETE FROM following "
                                 "WHERE username1 = ? AND username2 = ?",
                                 (logname, username2))

    return flask.redirect(target)


@insta485.app.route('/users/<user_url_slug>/followers/')
def followers(user_url_slug):
    """Display /users/<user_url_slug>/followers/ route."""
    username = user_url_slug

    # check if user is logged in
    if check_logged_in():
        return flask.redirect("/accounts/login/")
    user_logname = flask.session['username']

    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username, filename FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()
    if user is None:
        flask.abort(404)

    # Query database
    # very advanced stuff from chatgpt..
    # check whether the current_user follows the follower by counting # of rows
    # where username1 = user_url_slug and username2 = follower. If the count
    # is non 0, then the current user follows back and the value of
    # is_followed_back will be 1.

    # followers user->username
    query = """
        SELECT users.username, users.filename,
        (SELECT COUNT(*) FROM following
        WHERE username1 = ? AND username2 = users.username)
        as is_followed_back
        FROM users
        JOIN following ON following.username1 = users.username
        WHERE following.username2 = ?
    """

    cur = connection.execute(query, (user_logname, username))
    user_followers = cur.fetchall()

    # Add database info to context
    context = {"logname": user_logname, "followers": user_followers}
    return flask.render_template("followers.html", **context)


@insta485.app.route('/users/<user_url_slug>/following/')
def following(user_url_slug):
    """Display /users/<user_url_slug>/following/ route."""
    username = user_url_slug

    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname_user = flask.session['username']

    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username, filename FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()
    if user is None:
        flask.abort(404)

        # Query database
    # See followers(), only that the relationship is reversed

    query = """
        SELECT users.username, users.filename,
        (SELECT COUNT(*) FROM following
        WHERE username1 = ? AND username2 = users.username)
        as is_followed_back
        FROM users
        JOIN following ON following.username2 = users.username
        WHERE following.username1 = ?
    """

    cur = connection.execute(query, (logname_user, username))
    followings = cur.fetchall()

    # Add database info to context
    context = {"logname": logname_user, "followings": followings}
    return flask.render_template("following.html", **context)


@insta485.app.route('/explore/')
def explore():
    """Display /explore/ route."""
    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']

    connection = insta485.model.get_db()

    query = """SELECT username,filename FROM users
    WHERE username != ? AND NOT EXISTS (
    SELECT * FROM following
    WHERE following.username1 = ?
    AND following.username2 = users.username)
    """
    # can i select myself?

    not_following = connection.execute(query, (logname, logname)).fetchall()

    # Add database info to context
    context = {"logname": logname, "not_following": not_following}
    return flask.render_template("explore.html", **context)
