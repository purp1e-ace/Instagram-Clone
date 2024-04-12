"""
Insta485 index (main) view.

URLs include:
/
"""

import flask
import insta485


@insta485.app.route("/accounts/edit/")
def account_edit():
    """If logged in, redirect to /."""
    if "username" not in flask.session:
        return flask.redirect('/')

    connection = insta485.model.get_db()
    user_fullname = connection.execute(
        "SELECT fullname from users where username = ?",
        (flask.session['username'])
    )
    user_email = connection.execute(
        "SELECT email from users where username = ?",
        (flask.session['username'])
    )

    context = {"full_name": user_fullname, "user_email": user_email}

    # """Get it from the table ->
    # put into a variable -> send it to the renderer"""

    # """if not logged show login form"""
    return flask.render_template("login.html", **context)
