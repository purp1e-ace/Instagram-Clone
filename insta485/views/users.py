"""
Insta485 users (main) view.

URLs include:
/users/<user_url_slug>/
"""
import flask
import insta485
from insta485.views.helper import check_logged_in
from insta485.views.helper import get_logname


@insta485.app.route('/users/<user_url_slug>/')
def users(user_url_slug):
    """Users."""
    username = user_url_slug

    # check if user is logged in
    if check_logged_in():
        return flask.redirect("/accounts/login/")
    user_logname = get_logname()

    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username,fullname FROM users WHERE username = ?",
        (username,)
    )
    user = cur.fetchone()
    if user is None:
        flask.abort(404)

    # my homepage
    its_me = (user['username'] == user_logname)

    cur = connection.execute(
        "SELECT postid,filename FROM posts WHERE owner = ?",
        (username,)
    )
    posts_data = cur.fetchall()
    posts = {"count": len(posts_data), "data": posts_data}

    query = """SELECT
    SUM(CASE WHEN username1 = ? AND username2 = ?
    THEN 1 ELSE 0 END) im_following,
    SUM(CASE WHEN username2 = ? THEN 1 ELSE 0 END) ers,
    SUM(CASE WHEN username1 = ? THEN 1 ELSE 0 END) ing
    FROM following"""
    data = connection.execute(query, (user_logname, username,
                                      username, username)).fetchone()
    follow = {"ers": data['ers'], "ing": data['ing']}
    im_following = data['im_following']

    # Add database info to context
    context = {"logname": user_logname, "user": user,
               "im_following": im_following,
               "posts": posts, "follow": follow, "its_me": its_me}
    return flask.render_template("user.html", **context)
