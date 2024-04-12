"""
Insta485 index (main) view.

URLs include:
/
"""

import flask
import insta485


@insta485.app.route("/accounts/login/")
def account_login():
    """If logged in, redirect to /."""
    if "username" in flask.session:
        return flask.redirect('/')

    context = {}

    # """if not logged show login form"""
    return flask.render_template("login.html", **context)


@insta485.app.route("/accounts/logout/", methods=['POST'])
def account_logout():
    """Log out user."""
    del flask.session['username']

    # """Immediately redirect/."""
    return flask.redirect('/accounts/login/')


@insta485.app.route('/accounts/edit/')
def accounts_edit():
    """Display /accounts/edit/ route."""
    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']

    # Connect to database
    connection = insta485.model.get_db()
    cur = connection.execute(
        "SELECT username, filename, fullname, email "
        "FROM users WHERE username = ?",
        (logname,)
    )
    user = cur.fetchone()

    context = {'user': user}
    return flask.render_template('edit.html', **context)


@insta485.app.route('/accounts/password/')
def accounts_password():
    """Display /accounts/password/ route."""
    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']

    context = {'logname': logname}
    return flask.render_template('password.html', **context)


@insta485.app.route('/accounts/create/')
def accounts_create():
    """Display /accounts/create/ route."""
    # If there is a logged user, redirect to account edit page
    if 'username' in flask.session:
        return flask.redirect("/accounts/edit/")

    return flask.render_template('create.html')


@insta485.app.route('/accounts/delete/')
def accounts_delete():
    """Display /accounts/delete/ route."""
    # check if user is logged in
    if 'username' not in flask.session:
        return flask.redirect("/accounts/login/")
    logname = flask.session['username']

    context = {'logname': logname}
    return flask.render_template('delete.html', **context)
