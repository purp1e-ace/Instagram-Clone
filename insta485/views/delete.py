"""
Insta485 index (main) view.

URLs include:
/
"""

import flask
import insta485


@insta485.app.route("/accounts/delete/", methods=['GET', 'POST'])
def account_delete():
    """If logged in, redirect to /."""
    if "username" not in flask.session:
        return flask.redirect('/')

    context = {}

    # """if not logged show create form"""
    return flask.render_template("delete.html", **context)
