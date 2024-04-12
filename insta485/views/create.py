"""
Insta485 index (main) view.

URLs include:
/
"""

import flask
import insta485


@insta485.app.route("/accounts/create/", methods=['GET', 'POST'])
def account_create():
    """If logged in, redirect to /."""
    if "username" in flask.session:
        return flask.redirect('/')

    context = {}

    # """if not logged show create form"""

    return flask.render_template("create.html", **context)
